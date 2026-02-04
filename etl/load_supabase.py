import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

assert SUPABASE_URL, "SUPABASE_URL não encontrado"
assert SUPABASE_KEY, "SUPABASE_SERVICE_KEY não encontrado"


def get_supabase_client():
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


def upload_dataframe(
    df,
    table_name: str
):
    if df.empty:
        print("⚠️ DataFrame vazio. Nada para enviar.")
        return

    supabase = get_supabase_client()

    records = df.to_dict(orient="records")

    print(f"☁️ Enviando {len(records)} registros para '{table_name}' (UPSERT)...")

    try:
        supabase.table(table_name).upsert(
            records,
            on_conflict="ticker,data_referencia",
            ignore_duplicates=False
        ).execute()

        print("✅ Upload realizado com sucesso (UPSERT aplicado)")

    except Exception as e:
        print("❌ Erro ao enviar dados para o Supabase")
        raise e
