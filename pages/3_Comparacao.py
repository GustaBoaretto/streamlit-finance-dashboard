import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import loadfinancials

st.title("📊 Comparação de Empresas")

# ======================
# Carregar dados
# ======================
df = loadfinancials()
df["data_referencia"] = pd.to_datetime(df["data_referencia"])
df["ano"] = df["data_referencia"].dt.year

# ======================
# Seleção de setor
# ======================
setores = sorted(df["setor"].dropna().unique())
setor_sel = st.selectbox("Selecione o setor", setores)

df_setor = df[df["setor"] == setor_sel]
empresas = sorted(df_setor["empresa"].dropna().unique())

col1, col2 = st.columns(2)

# ======================
# Seletores
# ======================
with col1:
    empresa_a = st.selectbox("Empresa A", empresas, key="a")
    anos_a = sorted(df_setor[df_setor["empresa"] == empresa_a]["ano"].unique())
    ano_a = st.selectbox("Ano A", anos_a, key="ano_a")

with col2:
    empresa_b = st.selectbox("Empresa B", empresas, key="b")
    anos_b = sorted(df_setor[df_setor["empresa"] == empresa_b]["ano"].unique())
    ano_b = st.selectbox("Ano B", anos_b, key="ano_b")

dados_a = df_setor[(df_setor["empresa"] == empresa_a) & (df_setor["ano"] == ano_a)].iloc[0]
dados_b = df_setor[(df_setor["empresa"] == empresa_b) & (df_setor["ano"] == ano_b)].iloc[0]

# ======================
# Função normalização setorial
# ======================
def normalizar(valor, serie, inverter=False):
    p10 = serie.quantile(0.10)
    p90 = serie.quantile(0.90)

    if p90 == p10:
        score = 50
    else:
        score = (valor - p10) / (p90 - p10) * 100

    score = max(0, min(100, score))

    if inverter:
        score = 100 - score

    return score

# ======================
# Scorecard comparativo
# ======================
st.subheader("Scorecard Comparativo")

comparacao = pd.DataFrame({
    "Indicador":[
        "Liquidez Corrente",
        "Dívida Líq/EBITDA",
        "Endividamento",
        "Margem EBITDA",
        "ROE",
        "ICJ"
    ],
    f"{empresa_a} ({ano_a})":[
        dados_a["liquidez_corrente"],
        dados_a["divida_liquida_ebitda"],
        dados_a["endividamento"],
        dados_a["margem_ebitda"],
        dados_a["roe"],
        dados_a["icj"]
    ],
    f"{empresa_b} ({ano_b})":[
        dados_b["liquidez_corrente"],
        dados_b["divida_liquida_ebitda"],
        dados_b["endividamento"],
        dados_b["margem_ebitda"],
        dados_b["roe"],
        dados_b["icj"]
    ]
})

st.dataframe(comparacao, use_container_width=True)

# ======================
# Radar comparativo
# ======================
st.subheader("Radar Comparativo (Score Setorial)")

radar = pd.DataFrame({
    "categoria":[
        "Liquidez",
        "Rentabilidade",
        "Eficiência Operacional",
        "Estrutura de Capital",
        "Alavancagem",
        "ICJ"
    ]*2,
    "score":[
        normalizar(dados_a["liquidez_corrente"], df_setor["liquidez_corrente"]),
        normalizar(dados_a["roe"], df_setor["roe"]),
        normalizar(dados_a["margem_ebitda"], df_setor["margem_ebitda"]),
        normalizar(dados_a["endividamento"], df_setor["endividamento"], inverter=True),
        normalizar(dados_a["divida_liquida_ebitda"], df_setor["divida_liquida_ebitda"], inverter=True),
        normalizar(dados_a["icj"], df_setor["icj"]),

        normalizar(dados_b["liquidez_corrente"], df_setor["liquidez_corrente"]),
        normalizar(dados_b["roe"], df_setor["roe"]),
        normalizar(dados_b["margem_ebitda"], df_setor["margem_ebitda"]),
        normalizar(dados_b["endividamento"], df_setor["endividamento"], inverter=True),
        normalizar(dados_b["divida_liquida_ebitda"], df_setor["divida_liquida_ebitda"], inverter=True),
        normalizar(dados_b["icj"], df_setor["icj"])
    ],
    "Empresa":[
        f"{empresa_a} ({ano_a})"
    ]*6 + [
        f"{empresa_b} ({ano_b})"
    ]*6
})

fig = px.line_polar(
    radar,
    r="score",
    theta="categoria",
    color="Empresa",
    color_discrete_map={
        f"{empresa_a} ({ano_a})": "#ffc632",
        f"{empresa_b} ({ano_b})": "#007f3f"
    },
    line_close=True
)

fig.update_traces(fill="toself", opacity=0.5)
fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])))

st.plotly_chart(fig, use_container_width=True)