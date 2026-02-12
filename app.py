import os
import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

# -----------------------
# Configuração da página
# -----------------------
st.set_page_config(page_title="Perfil Estratégico de Mercado", layout="wide")

# -----------------------
# Secrets
# -----------------------
load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# Load data
# -----------------------
@st.cache_data(ttl=3600)
def load_data():
    response = supabase.table("vw_financials_enriched").select("*").execute()
    df = pd.DataFrame(response.data)
    df["data_referencia"] = pd.to_datetime(df["data_referencia"])
    return df

df = load_data()

# -----------------------
# HEADER
# -----------------------
st.title("📊 Perfil Estratégico de Mercado")
st.caption("Plataforma de monitoramento financeiro, comparação de empresas e análise estratégica baseada em dados")

st.divider()

# -----------------------
# SOBRE O PROJETO
# -----------------------
st.header("Sobre o projeto")

st.markdown("""
Este projeto tem como objetivo consolidar **dados financeiros, indicadores setoriais e notícias de mercado**
em uma plataforma única de análise estratégica.

A aplicação permite:

- Monitorar a evolução financeira das empresas
- Comparar empresas dentro do mesmo setor
- Avaliar posição competitiva relativa ao mercado
- Identificar tendências de crescimento e rentabilidade
- Gerar insights quantitativos para suporte à tomada de decisão
""")

# -----------------------
# VISÃO GERAL DOS DADOS
# -----------------------
st.header("Base de dados")

col1, col2, col3 = st.columns(3)

col1.metric("Empresas monitoradas", df["empresa"].nunique())
col2.metric("Setores", df["setor"].nunique())
col3.metric("Observações históricas", len(df))

# -----------------------
# ABAS DO SISTEMA
# -----------------------
st.header("Navegação da plataforma")

st.markdown("""
A plataforma está organizada nas seguintes páginas:
            
### 📈 Monitoramento do Setor
- Tendências agregadas por setor
- Rankings automáticos
- Indicadores médios de mercado
            
### 📊 Análise da Empresa
- Scorecard financeiro automático
- Radar comparativo com o setor
- Indicadores de rentabilidade, liquidez e endividamento
- Notícias recentes relacionadas à empresa

### ⚖️ Comparação de Empresas
- Comparação entre duas empresas
- Comparação da mesma empresa em anos diferentes (ex: 2023 vs 2024)
- Radar comparativo de indicadores financeiros


Use o menu lateral para navegar entre as análises.
""")

st.info("Este projeto é atualizado automaticamente conforme novas divulgações financeiras são disponibilizadas.")
