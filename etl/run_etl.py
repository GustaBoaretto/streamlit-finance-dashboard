from data.empresas import get_empresas_df
from etl.extract import extract_empresas
from etl.transform import transform_financials

from pathlib import Path

# ============================
# Paths
# ============================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

ARQ_SAIDA = DATA_PROCESSED / "indicadores.parquet"

# ============================
# Pipeline
# ============================

print("Carregando empresas...")
empresas_df = get_empresas_df()

print("Extraindo dados do Yahoo Finance...")
df_raw = extract_empresas(empresas_df)
print(df_raw.head())

print("Transformando indicadores...")
df_final = transform_financials(df_raw)
print(df_final.head())

print("Salvando arquivo...")
df_final.to_parquet(ARQ_SAIDA, index=False)

print(f"ETL concluído: {ARQ_SAIDA}")

