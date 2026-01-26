import streamlit as st
import pandas as pd
from utils.news import get_news

# -----------------------
# Configuração da página
# -----------------------
st.set_page_config(
    page_title="📊 Finance Dashboard",
    layout="wide"
)

st.title("📊 Relatório Financeiro por Setor")

# -----------------------
# Leitura dos dados
# -----------------------
@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/indicadores.parquet")

df = load_data()

# -----------------------
# Sidebar - Filtros
# -----------------------
st.sidebar.header("🎯 Filtros")

setores = st.sidebar.multiselect(
    "Setor",
    options=sorted(df["Setor"].dropna().unique())
)

subsetores = st.sidebar.multiselect(
    "Subsetor",
    options=sorted(df["Subsetor"].dropna().unique())
)

empresas = st.sidebar.multiselect(
    "Empresa",
    options=sorted(df["Empresa"].dropna().unique())
)

df_filtro = df.copy()

if setores:
    df_filtro = df_filtro[df_filtro["Setor"].isin(setores)]

if subsetores:
    df_filtro = df_filtro[df_filtro["Subsetor"].isin(subsetores)]

if empresas:
    df_filtro = df_filtro[df_filtro["Empresa"].isin(empresas)]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores Médios")

col1, col2, col3, col4, col5 = st.columns(5)

def safe_mean(col):
    return df_filtro[col].dropna().mean() if col in df_filtro else None

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
    ["Market Cap", "ROE", "Margem EBITDA", "Liquidez Corrente"]
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
    ["ROE", "Margem EBITDA", "Market Cap", "Liquidez Corrente"]
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
    for empresa in empresas_selecionadas[:5]:  # limita para não sobrecarregar
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
