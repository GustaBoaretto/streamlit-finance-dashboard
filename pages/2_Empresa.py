import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.db import loadfinancials
from utils.news import get_news

st.set_page_config(layout="wide")
st.title("🏢 Análise da Empresa")

# ======================
# LOAD DATA
# ======================
df_all = loadfinancials()

# ======================
# FILTROS
# ======================
setores = sorted(df_all["setor"].dropna().unique())
setor_sel = st.selectbox("Selecione o setor", setores)

df_setor = df_all[df_all["setor"] == setor_sel]

empresas = sorted(df_setor["empresa"].dropna().unique())
empresa_sel = st.selectbox("Selecione a empresa", empresas)

df_empresa = df_setor[df_setor["empresa"] == empresa_sel].sort_values("data_referencia")
ultimo = df_empresa.iloc[-1]

# ======================
# NORMALIZAÇÃO SETORIAL
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
# SEMÁFORO SETORIAL
# ======================
def semaforo_setorial(valor, serie, inverter=False):

    p33 = serie.quantile(0.33)
    p66 = serie.quantile(0.66)

    if inverter:
        if valor <= p33:
            return "🟢"
        elif valor <= p66:
            return "🟡"
        else:
            return "🔴"
    else:
        if valor >= p66:
            return "🟢"
        elif valor >= p33:
            return "🟡"
        else:
            return "🔴"

# ======================
# LAYOUT
# ======================
col_news, col_main = st.columns([1,2])

# ======================
# NEWS
# ======================
with col_news:
    st.subheader("📰 Notícias")

    noticias = get_news(empresa_sel, limit=8)

    if noticias:
        for n in noticias:
            st.markdown(f"**[{n['title']}]({n['link']})**")
            st.caption(n.get("published",""))
            st.divider()
    else:
        st.info("Nenhuma notícia encontrada")

# ======================
# SCORECARD + RADAR
# ======================
with col_main:

    st.subheader("Scorecard da Empresa")

    tabela = pd.DataFrame({
        "Indicador":[
            "Liquidez Corrente",
            "Dívida Líq/EBITDA",
            "Endividamento",
            "Margem EBITDA",
            "ROE"
        ],
        "Valor":[
            ultimo["liquidez_corrente"],
            ultimo["divida_liquida_ebitda"],
            ultimo["endividamento"],
            ultimo["margem_ebitda"],
            ultimo["roe"]
        ]
    })

    tabela["Sinal"] = [
        semaforo_setorial(ultimo["liquidez_corrente"], df_setor["liquidez_corrente"]),
        semaforo_setorial(ultimo["divida_liquida_ebitda"], df_setor["divida_liquida_ebitda"], inverter=True),
        semaforo_setorial(ultimo["endividamento"], df_setor["endividamento"], inverter=True),
        semaforo_setorial(ultimo["margem_ebitda"], df_setor["margem_ebitda"]),
        semaforo_setorial(ultimo["roe"], df_setor["roe"])
    ]

    st.dataframe(tabela, use_container_width=True, hide_index=True)

    # ======================
    # RADAR
    # ======================
    st.subheader("Radar de Indicadores (Empresa vs Mercado)")

    radar = pd.DataFrame({
        "categoria":[
            "Liquidez",
            "Rentabilidade",
            "Eficiência Operacional",
            "Estrutura de Capital",
            "Alavancagem",
            "Capacidade de Pagamento"
        ]
    })

    radar["Empresa Score"] = [
        normalizar(ultimo["liquidez_corrente"], df_setor["liquidez_corrente"]),
        normalizar(ultimo["roe"], df_setor["roe"]),
        normalizar(ultimo["margem_ebitda"], df_setor["margem_ebitda"]),
        normalizar(ultimo["endividamento"], df_setor["endividamento"], inverter=True),
        normalizar(ultimo["divida_liquida_ebitda"], df_setor["divida_liquida_ebitda"], inverter=True),
        normalizar(ultimo["liquidez_corrente"], df_setor["liquidez_corrente"])
    ]

    radar["Mercado Score"] = [
        normalizar(df_setor["liquidez_corrente"].mean(), df_setor["liquidez_corrente"]),
        normalizar(df_setor["roe"].mean(), df_setor["roe"]),
        normalizar(df_setor["margem_ebitda"].mean(), df_setor["margem_ebitda"]),
        normalizar(df_setor["endividamento"].mean(), df_setor["endividamento"], inverter=True),
        normalizar(df_setor["divida_liquida_ebitda"].mean(), df_setor["divida_liquida_ebitda"], inverter=True),
        normalizar(df_setor["liquidez_corrente"].mean(), df_setor["liquidez_corrente"])
    ]

    # ======================
    # SCORE ÚNICO + RANKING
    # ======================
    score_empresa = radar["Empresa Score"].mean()

    # calcular score para todas empresas do setor
    ultimos = (
        df_setor.sort_values("data_referencia")
        .groupby("empresa")
        .tail(1)
        .copy()
    )

    def calcular_score(row):
        scores = [
            normalizar(row["liquidez_corrente"], df_setor["liquidez_corrente"]),
            normalizar(row["roe"], df_setor["roe"]),
            normalizar(row["margem_ebitda"], df_setor["margem_ebitda"]),
            normalizar(row["endividamento"], df_setor["endividamento"], inverter=True),
            normalizar(row["divida_liquida_ebitda"], df_setor["divida_liquida_ebitda"], inverter=True)
        ]
        return np.mean(scores)

    ultimos["score"] = ultimos.apply(calcular_score, axis=1)
    ultimos["ranking"] = ultimos["score"].rank(ascending=False)

    posicao = int(ultimos.loc[ultimos["empresa"] == empresa_sel, "ranking"].iloc[0])

    col_score1, col_score2 = st.columns(2)

    col_score1.metric("Company Quality Score", f"{score_empresa:.1f}")
    col_score2.metric("Ranking no setor", f"{posicao} / {len(ultimos)}")

    radar_plot = radar.melt(id_vars="categoria", var_name="grupo", value_name="score")

    fig = px.line_polar(
        radar_plot,
        r="score",
        theta="categoria",
        color="grupo",
        line_close=True,
        color_discrete_map={
            "Empresa Score": "#2f90d6",
            "Mercado Score": "green"
        }
    )

    fig.update_traces(fill='toself', opacity=0.4)
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])))

    st.plotly_chart(fig, use_container_width=True)
