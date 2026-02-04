from data.empresas import get_empresas_df
from etl.extract import extract_empresas
from etl.transform import transform_financials

from pathlib import Path
from datetime import date
import pandas as pd

# ============================
# Configurações
# ============================

SAVE_CSV = True
SAVE_PARQUET = False   # opcional
TEST_RUN = True        # flag semântica

# ============================
# Paths
# ============================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = BASE_DIR / "data" / "processed" / "test"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

DATA_REF = date.today().replace(day=1)

ARQ_CSV = DATA_PROCESSED / f"indicadores_financeiros_test_{DATA_REF}.csv"
ARQ_PARQUET = DATA_PROCESSED / f"indicadores_financeiros_test_{DATA_REF}.parquet"

# ============================
# Pipeline
# ============================

print("Iniciando ETL — MODO TESTE (SEM SUPABASE)")

# 1. Extract
print("Carregando empresas...")
empresas_df = get_empresas_df()
print(f"Empresas carregadas: {len(empresas_df)}")

print("Extraindo dados do Yahoo Finance...")
df_raw = extract_empresas(empresas_df)

print("Preview extract:")
print(df_raw.head())
print(f"Linhas extraídas: {len(df_raw)}")

# 2. Transform
print("Transformando indicadores financeiros...")
df_final = transform_financials(df_raw)

# ============================
# Data de referência (igual ao modelo produtivo)
# ============================

df_final["data_referencia"] = DATA_REF

# ============================
# Normalização de colunas (igual ao banco)
# ============================

df_final.columns = (
    df_final.columns
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.replace(" ", "_")
        .str.replace("/", "_")
)

print("Preview transform (final):")
print(df_final.head())
print("Colunas finais:")
print(list(df_final.columns))

# ============================
# Salvamento local (TESTE)
# ============================

if SAVE_CSV:
    print("Salvando CSV de teste...")
    df_final.to_csv(
        ARQ_CSV,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )
    print(f"CSV salvo em: {ARQ_CSV}")

if SAVE_PARQUET:
    print("Salvando Parquet de teste...")
    df_final.to_parquet(ARQ_PARQUET, index=False)
    print(f"Parquet salvo em: {ARQ_PARQUET}")

print("ETL de TESTE finalizada com sucesso!")
