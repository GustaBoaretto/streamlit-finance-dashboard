import pandas as pd
from datetime import datetime, timezone

FONTE_PADRAO = "yfinance"

empresas = [

    # ============================================
    # 1) DISTRIBUIÇÃO DE COMBUSTÍVEIS
    # ============================================
    {"setor": "Distribuição de Combustíveis", "tipo": "Estratégico", "empresa": "Raízen", "ticker": "RAIZ4.SA", "moeda": "BRL"},
    {"setor": "Distribuição de Combustíveis", "tipo": "Estratégico", "empresa": "Ipiranga (via Ultrapar)", "ticker": "UGPA3.SA", "moeda": "BRL"},
    {"setor": "Distribuição de Combustíveis", "tipo": "Estratégico", "empresa": "Vibra Energia", "ticker": "VBBR3.SA", "moeda": "BRL"},

    {"setor": "Distribuição de Combustíveis", "tipo": "Demais", "empresa": "AirBP (via BP plc)", "ticker": "BP", "moeda": "USD"},
    {"setor": "Distribuição de Combustíveis", "tipo": "Demais", "empresa": "ALE (via Glencore)", "ticker": "GLEN.L", "moeda": "GBP"},


    # ============================================
    # 2) E&P PETRÓLEO E GÁS
    # ============================================
    {"setor": "E&P Petróleo e Gás", "tipo": "Estratégico", "empresa": "Petrobras", "ticker": "PETR4.SA", "moeda": "BRL"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Estratégico", "empresa": "Brava Energia", "ticker": "BRAV3.SA", "moeda": "BRL"},

    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "Shell (controladora)", "ticker": "SHEL", "moeda": "USD"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "PRIO (ex-PetroRio)", "ticker": "PRIO3.SA", "moeda": "BRL"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "Maha Energy", "ticker": "MAHA-A.ST", "moeda": "SEK"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "TotalEnergies", "ticker": "TTE", "moeda": "USD"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "Equinor (BDR Brasil)", "ticker": "E1QN34.SA", "moeda": "BRL"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "Petrogal (Galp Energia)", "ticker": "GALP.LS", "moeda": "EUR"},
    {"setor": "E&P Petróleo e Gás", "tipo": "Demais", "empresa": "Repsol", "ticker": "REP.MC", "moeda": "EUR"},

    # ============================================
    # 3) PETROQUÍMICA
    # ============================================
    {"setor": "Petroquímica", "tipo": "Estratégico", "empresa": "Braskem", "ticker": "BRKM5.SA", "moeda": "BRL"},

    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "Unipar", "ticker": "UNIP6.SA", "moeda": "BRL"},
    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "Oxiteno (Indorama)", "ticker": "IVL.BK", "moeda": "THB"},
    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "Dow", "ticker": "DOW", "moeda": "USD"},
    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "BASF", "ticker": "BAS.DE", "moeda": "EUR"},
    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "Suzano", "ticker": "SUZB3.SA", "moeda": "BRL"},
    {"setor": "Petroquímica", "tipo": "Demais", "empresa": "Alpek", "ticker": "ALPKF", "moeda": "USD"},

    # ============================================
    # 4) DISTRIBUIÇÃO DE ENERGIA
    # ============================================
    {"setor": "Distribuição de Energia", "tipo": "Estratégico", "empresa": "Coelba", "ticker": "CEEB3.SA", "moeda": "BRL"},
    {"setor": "Distribuição de Energia", "tipo": "Demais", "empresa": "Eneva", "ticker": "ENEV3.SA", "moeda": "BRL"},
    {"setor": "Distribuição de Energia", "tipo": "Demais", "empresa": "Engie Brasil", "ticker": "EGIE3.SA", "moeda": "BRL"},
    {"setor": "Distribuição de Energia", "tipo": "Demais", "empresa": "Ômega Energia(Serena Energia)", "ticker": "SRNA3", "moeda": "BRL"},

    # ============================================
    # 5) LOGÍSTICA
    # ============================================
    {"setor": "Logística de Combustíveis", "tipo": "Demais", "empresa": "Rumo", "ticker": "RAIL3.SA", "moeda": "BRL"},
    {"setor": "Logística de Combustíveis", "tipo": "Demais", "empresa": "Hidrovias do Brasil", "ticker": "HBSA3.SA", "moeda": "BRL"},
    {"setor": "Logística de Combustíveis", "tipo": "Demais", "empresa": "Santos Brasil", "ticker": "STOSF", "moeda": "USD"},
    {"setor": "Logística de Combustíveis", "tipo": "Demais", "empresa": "Vopak", "ticker": "VPK.AS", "moeda": "EUR"},

    # ============================================
    # 6) GÁS
    # ============================================
    {"setor": "Gás e Energia", "tipo": "Demais", "empresa": "New Fortress Energy", "ticker": "NFE", "moeda": "USD"},
]


def get_empresas_df() -> pd.DataFrame:
    df = pd.DataFrame(empresas)

    df["fonte"] = FONTE_PADRAO
    df["data_atualizacao"] = datetime.now(timezone.utc)

    return df[
        ["ticker", "empresa", "setor", "tipo", "fonte", "data_atualizacao", "moeda"]
    ]
