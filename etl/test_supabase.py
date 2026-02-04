import os
from dotenv import load_dotenv
from supabase import create_client

# Carrega variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

assert SUPABASE_URL, "SUPABASE_URL não encontrado"
assert SUPABASE_KEY, "SUPABASE_SERVICE_KEY não encontrado"

# Cria client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Teste simples(apenas validar conexão)
response = supabase.table("financials_gold").select("*").limit(1).execute()

print("Conexão OK!")
print(response)
