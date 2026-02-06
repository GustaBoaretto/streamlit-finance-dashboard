import os
import streamlit as st
import pandas as pd
from supabase import create_client
from utils.news import get_news
from dotenv import load_dotenv

# -----------------------
# Configuração da página
# -----------------------
st.set_page_config(
    page_title="📊 Finance Dashboard",
    layout="wide"
)

st.title("📊 Relatório Financeiro por Setor")

# -----------------------
# Supabase connection
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
# Leitura dos dados
# -----------------------
@st.cache_data(ttl=3600)
def load_data():

    response = (
        supabase
        .table("vw_financials_enriched")
        .select("*")
        .execute()
    )

    df = pd.DataFrame(response.data)

    # padronização nomes para compatibilidade com dashboard
    df.rename(columns={
        "empresa": "Empresa",
        "setor": "Setor",
        "roe": "ROE",
        "margem_ebitda": "Margem EBITDA",
        "liquidez_corrente": "Liquidez Corrente",
        "endividamento": "Endividamento"
    }, inplace=True)

    return df

df = load_data()

# -----------------------
# Sidebar - Filtros
# -----------------------
st.sidebar.header("🎯 Filtros")

setores = st.sidebar.multiselect(
    "Setor",
    options=sorted(df["Setor"].dropna().unique())
)

empresas = st.sidebar.multiselect(
    "Empresa",
    options=sorted(df["Empresa"].dropna().unique())
)

df_filtro = df.copy()

if setores:
    df_filtro = df_filtro[df_filtro["Setor"].isin(setores)]


if empresas:
    df_filtro = df_filtro[df_filtro["Empresa"].isin(empresas)]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores Médios")

col1, col2, col3, col4, col5 = st.columns(5)

def safe_mean(col):
    return df_filtro[col].dropna().mean() if col in df_filtro else 0

col1.metric("💰 Market Cap Médio", f"{safe_mean('Market Cap'):,.0f}")
col2.metric("📈 ROE Médio", f"{safe_mean('ROE'):.2%}")
col3.metric("🧮 Margem EBITDA", f"{safe_mean('Margem EBITDA'):.2%}")
col4.metric("🏦 Liquidez Corrente", f"{safe_mean('Liquidez Corrente'):.2f}")
col5.metric("⚠️ Endividamento", f"{safe_mean('Endividamento'):.2f}")

# -----------------------
# Ranking de Empresas
# -----------------------
st.subheader("🏆 Ranking de Empresas")

ranking_col = st.selectbox(
    "Ordenar por:",
    [ "ROE", "Margem EBITDA", "Liquidez Corrente"]
)

ranking = (
    df_filtro[["Empresa", "Setor", ranking_col]]
    .dropna()
    .sort_values(by=ranking_col, ascending=False)
)

st.dataframe(ranking, use_container_width=True)

# -----------------------
# Gráficos
# -----------------------
st.subheader("📊 Visualização")

grafico_col = st.selectbox(
    "Indicador para gráfico:",
    ["ROE", "Margem EBITDA", "Liquidez Corrente"]
)

chart_df = (
    df_filtro[["Empresa", grafico_col]]
    .dropna()
    .sort_values(by=grafico_col, ascending=False)
)

st.bar_chart(chart_df.set_index("Empresa"))

# -----------------------
# Notícias das Empresas
# -----------------------
st.subheader("Últimas Notícias")

empresas_selecionadas = (
    empresas if empresas else df_filtro["Empresa"].dropna().unique().tolist()
)

if not empresas_selecionadas:
    st.info("Selecione ao menos uma empresa para visualizar notícias.")
else:
    for empresa in empresas_selecionadas[:5]:
        st.markdown(f"### 🏢 {empresa}")

        try:
            noticias = get_news(empresa, limit=5)

            if not noticias:
                st.caption("Nenhuma notícia encontrada.")
                continue

            for n in noticias:
                st.markdown(
                    f"""
                    - **[{n['title']}]({n['link']})**  
                      <small>{n['published']}</small>
                    """,
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"Erro ao buscar notícias para {empresa}: {e}")
