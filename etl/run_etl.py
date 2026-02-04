from data.empresas import get_empresas_df
from etl.extract import extract_empresas
from etl.transform import transform_financials, transform_tickers_metadata
from etl.load_supabase import upload_dataframe, get_supabase_client

from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# ============================
# Configurações
# ============================

SAVE_LOCAL_PARQUET = False
TABLE_NAME = "financials_gold"
METADATA_TABLE = "tickers_metadata"

# ============================
# Paths (backup local)
# ============================ 

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

ARQ_SAIDA = DATA_PROCESSED / "indicadores.parquet"

# ============================
# Funções auxiliares
# ============================

def drop_rows_with_nan_and_log(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas que possuem qualquer NaN e imprime
    ticker + data_referencia das linhas removidas.
    """
    df = df.copy()
    mask_nan = df.isna().any(axis=1)

    if mask_nan.any():
        print("⚠️ Linhas removidas por conter NaN:")
        cols_log = [c for c in ["ticker", "data_referencia"] if c in df.columns]

        print(
            df.loc[mask_nan, cols_log]
              .drop_duplicates()
              .to_string(index=False)
        )

        print(f"🗑️ Total de linhas removidas: {mask_nan.sum()}")
    else:
        print("✅ Nenhuma linha com NaN encontrada.")

    return df.loc[~mask_nan].reset_index(drop=True)


def prepare_df_for_json(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d")
        elif df[col].apply(lambda x: hasattr(x, "isoformat")).any():
            df[col] = df[col].apply(
                lambda x: x.isoformat() if x is not None else None
            )

    df.replace([np.inf, -np.inf, pd.NA, pd.NaT], None, inplace=True)
    df = df.where(pd.notna(df), None)
    return df


def upsert_tickers_metadata(df: pd.DataFrame):
    print("🧩 Sincronizando tickers_metadata...")

    # ==================================================
    # COLUNAS ESPERADAS NA TABELA AUXILIAR
    # ==================================================
    expected_cols = [
        "ticker",
        "empresa",
        "setor",
        "subsetor",
        "market_cap",
        "preco",
    ]

    # ==================================================
    # VALIDAÇÃO MÍNIMA
    # ==================================================
    if "ticker" not in df.columns:
        raise ValueError("❌ Coluna obrigatória 'ticker' não encontrada no DataFrame")

    # usa apenas as colunas que realmente existem
    cols_present = [c for c in expected_cols if c in df.columns]

    if not cols_present:
        raise ValueError("❌ Nenhuma coluna válida encontrada para tickers_metadata")

    # ==================================================
    # SELEÇÃO + DEDUPLICAÇÃO
    # ==================================================
    metadata_df = (
        df[cols_present]
        .dropna(subset=["ticker"])
        .drop_duplicates(subset=["ticker"])
        .copy()
    )

    # ==================================================
    # DATA DE ATUALIZAÇÃO (UTC / JSON SAFE)
    # ==================================================
    metadata_df["data_atualizacao"] = datetime.now(timezone.utc).isoformat()

    # ==================================================
    # LIMPEZA FINAL (POSTGRES / SUPABASE SAFE)
    # ==================================================
    metadata_df.replace(
        [np.inf, -np.inf, pd.NA, pd.NaT],
        None,
        inplace=True
    )

    metadata_df = metadata_df.where(pd.notna(metadata_df), None)

    records = metadata_df.to_dict(orient="records")

    if not records:
        print("⚠️ Nenhum registro válido para sincronizar")
        return

    # ==================================================
    # UPSERT NO SUPABASE
    # ==================================================
    supabase = get_supabase_client()

    supabase.table("tickers_metadata").upsert(
        records,
        on_conflict="ticker"
    ).execute()

    print(f"✅ {len(records)} tickers sincronizados em tickers_metadata")

# ============================
# Pipeline
# ============================

print("🚀 Iniciando ETL")

# 1. Extract
print("📥 Carregando empresas...")
empresas_df = get_empresas_df()

print("📊 Extraindo dados do Yahoo Finance...")
df_raw = extract_empresas(empresas_df)

# 2. Transform
print("🔧 Transformando indicadores...")
df_final = transform_financials(df_raw)

# 2. Transform para a base auxiliar
df_final_ts = transform_tickers_metadata(df_raw)
# ============================
# Normalização de colunas
# ============================

df_final.columns = (
    df_final.columns
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("__+", "_", regex=True)
        .str.strip("_")
)

# ============================
# Arredondamento financeiro
# ============================

NUMERIC_2 = [
    "ativo_total", "passivo_total", "patrimonio_liquido",
    "ativo_circulante", "passivo_circulante",
    "ativo_nao_circulante", "passivo_nao_circulante",
    "divida_total", "caixa_total", "divida_liquida",
    "ebit", "ebitda", "ebitda_ajustado",
    "receita_liquida", "despesa_de_juros", "lucro_liquido"
]

NUMERIC_4 = [
    "liquidez_corrente", "icj", "icj_ajustado",
    "divida_liquida_ebitda", "divida_liquida_ebitda_ajustado",
    "endividamento", "endividamento_ajustado",
    "margem_ebitda", "roe", "roe_ajustado"
]

for col in NUMERIC_2:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(float).round(2)

for col in NUMERIC_4:
    if col in df_final.columns:
        df_final[col] = df_final[col].astype(float).round(4)

# ============================
# Data de carga
# ============================

df_final["data_carga"] = datetime.now(timezone.utc)

# ============================
# Limpeza de inválidos
# ============================

df_final.replace([np.inf, -np.inf], np.nan, inplace=True)
df_final = drop_rows_with_nan_and_log(df_final)
df_final = prepare_df_for_json(df_final)

# ============================
# Diagnósticos finais
# ============================

dup_mask = df_final[["ticker", "data_referencia"]].duplicated()

print("📊 Diagnóstico de duplicados (ticker, data_referencia):")
print(dup_mask.value_counts())

if dup_mask.any():
    print(df_final.loc[dup_mask, ["ticker", "data_referencia", "empresa"]])
else:
    print("✅ Nenhum registro duplicado encontrado.")

# ============================
# Load - Supabase
# ============================

print("☁️ Enviando dados para o Supabase (financials_gold)...")

upload_dataframe(
    df=df_final,
    table_name=TABLE_NAME
)

upsert_tickers_metadata(df_final_ts)

print("✅ Upload concluído!")

# ============================
# Backup local (opcional)
# ============================

if SAVE_LOCAL_PARQUET:
    df_final.to_parquet(ARQ_SAIDA, index=False)
    print(f"💾 Backup salvo em: {ARQ_SAIDA}")

print("🏁 ETL finalizada com sucesso!")