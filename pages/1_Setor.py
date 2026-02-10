import streamlit as st
from utils.db import loadfinancials
from utils.news import get_news
# from utils.llm import summarize_news   # desabilitado temporariamente

st.title("📊 Inteligência por Setor")

# ----------------------
# Seleção do setor
# ----------------------
df_all = loadfinancials()

if df_all.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

setores = sorted(df_all["setor"].dropna().unique())
setor = st.selectbox("Selecione o setor", setores)

if not setor:
    st.stop()

df_setor = loadfinancials(setor=setor)

# ----------------------
# Layout em colunas
# ----------------------
col_news, col_main = st.columns([1, 2])

# ======================
# COLUNA ESQUERDA — Notícias
# ======================
with col_news:
    st.subheader("📰 Notícias do Setor")

    news = get_news(setor, limit=10)

    all_text = ""

    for n in news:
        st.markdown(f"**[{n['title']}]({n['link']})**")
        st.caption(n["published"])
        all_text += f"{n['title']} {n.get('summary','')} "

# ======================
# COLUNA DIREITA — Dados
# ======================
with col_main:

    st.subheader("📈 Indicadores Financeiros do Setor")

    col1, col2, col3 = st.columns(3)

    col1.metric("ROE médio", f"{df_setor['roe'].mean():.2%}")
    col2.metric("Margem EBITDA média", f"{df_setor['margem_ebitda'].mean():.2%}")
    col3.metric("Endividamento médio", f"{df_setor['endividamento'].mean():.2f}")

    st.dataframe(df_setor, use_container_width=True)

    # ----------------------
    # Insight IA (desabilitado)
    # ----------------------
    st.subheader("🧠 Insight gerado por IA do Setor")
    st.warning("⚠️ Insight gerado por IA temporariamente desabilitado para manutenção.")
