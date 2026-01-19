from data.empresas import get_empresas_df
from etl.extract import extract_empresas

empresas_df = get_empresas_df()

df_final = extract_empresas(empresas_df)

print(df_final.head())
