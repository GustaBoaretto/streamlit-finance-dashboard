import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import loadfinancials
from utils.news import get_news
from datetime import datetime

st.title("📊 Inteligência por Setor")

# ----------------------
# Load dados
# ----------------------
df_all = loadfinancials()

if df_all.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df_all["data_referencia"] = pd.to_datetime(df_all["data_referencia"])
df_all["ano"] = df_all["data_referencia"].dt.year

# ----------------------
# Seleção do setor
# ----------------------
setores = sorted(df_all["setor"].dropna().unique())
setor = st.selectbox("Selecione o setor", setores)

df_setor = df_all[df_all["setor"] == setor]

# ----------------------
# Seleção do ano
# ----------------------
anos = sorted(df_setor["ano"].unique())
ano_sel = st.selectbox("Selecione o ano", anos)

df_ano = df_setor[df_setor["ano"] == ano_sel]

# ----------------------
# Layout
# ----------------------
col_news, col_main = st.columns([1, 2])

# ======================
# COLUNA ESQUERDA — Notícias
# ======================
with col_news:
    st.subheader("📰 Notícias do Setor")

    if "news_limit" not in st.session_state:
        st.session_state.news_limit = 10

    news = get_news(setor, limit=st.session_state.news_limit)

    # converter e ordenar por data (mais recente primeiro)
    news_sorted = sorted(
        news,
        key=lambda x: datetime.strptime(
        x["published"],
        "%a, %d %b %Y %H:%M:%S %Z"
        ),
        reverse=True
    )

    news_html = ""

    for n in news_sorted:
        news_html += f"""
        <div style="margin-bottom:15px">
            <a href="{n['link']}" target="_blank"><b>{n['title']}</b></a><br>
            <small>{n['published']}</small>
        </div>
        <hr>
        """

    st.markdown(
        f"""
        <div style="
            height:400px;
            overflow-y:auto;
            padding-right:10px;
            border:1px solid rgba(200,200,200,0.2);
            border-radius:6px;
            padding:10px;
        ">
        {news_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("⬇️ Carregar notícias mais antigas"):
        st.session_state.news_limit += 10
        st.rerun()
# ======================
# COLUNA DIREITA — Dados
# ======================
with col_main:

    st.subheader("📈 Snapshot do Setor")

    col1, col2, col3 = st.columns(3)

    col1.metric("ROE médio", f"{df_ano['roe'].mean():.2%}")
    col2.metric("Margem EBITDA média", f"{df_ano['margem_ebitda'].mean():.2%}")
    col3.metric("Endividamento médio", f"{df_ano['endividamento'].mean():.2f}")

    st.divider()

    # =====================================================
    # 📊 DISTRIBUIÇÃO DO SETOR
    # =====================================================
    st.subheader("📊 Distribuição dos Indicadores")

    cols = ["roe", "margem_ebitda", "endividamento"]

    for c in cols:
        df_ano[c] = pd.to_numeric(df_ano[c], errors="coerce")

    box_df = df_ano[["empresa"] + cols].melt(
        id_vars="empresa",
        var_name="Indicador",
        value_name="Valor"
    ).dropna()

    fig_box = px.box(
        box_df,
        x="Indicador",
        y="Valor",
        points="outliers",
        hover_data=["empresa"]
    )

    st.plotly_chart(fig_box, use_container_width=True)

    st.divider()

    # =====================================================
    # 🧭 MAPA DE POSICIONAMENTO COMPETITIVO
    # =====================================================
    st.subheader("🧭 Mapa de Posicionamento Competitivo")

    fig_scatter = px.scatter(
        df_ano,
        x="endividamento",
        y="roe",
        size="receita_liquida",
        hover_name="empresa",
        hover_data={
            "roe":":.2%",
            "endividamento":":.2f",
            "receita_liquida":":,.0f"
        },
        labels={
            "roe":"ROE",
            "endividamento":"Endividamento",
            "receita_liquida":"Receita Líquida"
        }
    )

    fig_scatter.add_vline(
        x=df_ano["endividamento"].mean(),
        line_dash="dash"
    )

    fig_scatter.add_hline(
        y=df_ano["roe"].mean(),
        line_dash="dash"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    st.subheader("🧠 Insight gerado por IA do Setor")
    st.warning("⚠️ Insight gerado por IA temporariamente desabilitado para manutenção.")
