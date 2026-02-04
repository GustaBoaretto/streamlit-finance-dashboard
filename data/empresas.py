import pandas as pd

# ============================================
# Base de empresas
# ============================================

empresas = [

    # ============================================
    # 1) DISTRIBUIÇÃO DE COMBUSTÍVEIS
    # ============================================
    {"Setor": "Distribuição de Combustíveis", "Tipo": "Estratégico", "Empresa": "Raízen",                  "Ticker": "RAIZ4.SA"},
    {"Setor": "Distribuição de Combustíveis", "Tipo": "Estratégico", "Empresa": "Ipiranga (via Ultrapar)", "Ticker": "UGPA3.SA"},
    {"Setor": "Distribuição de Combustíveis", "Tipo": "Estratégico", "Empresa": "Vibra Energia",           "Ticker": "VBBR3.SA"},

    {"Setor": "Distribuição de Combustíveis", "Tipo": "Demais", "Empresa": "AirBP (via BP plc)",        "Ticker": "BP"},
    {"Setor": "Distribuição de Combustíveis", "Tipo": "Demais", "Empresa": "ALE (via Glencore)",        "Ticker": "GLEN.L"},


    # ============================================
    # 2) E&P PETRÓLEO E GÁS
    # ============================================
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Estratégico", "Empresa": "Petrobras PN",  "Ticker": "PETR4.SA"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Estratégico", "Empresa": "Brava Energia", "Ticker": "BRAV3.SA"},

    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "Shell (controladora)",    "Ticker": "SHEL"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "PRIO (ex-PetroRio)",      "Ticker": "PRIO3.SA"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "Maha Energy",             "Ticker": "MAHA-A.ST"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "TotalEnergies",           "Ticker": "TTE"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "Equinor (BDR Brasil)",    "Ticker": "E1QN34.SA"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "Petrogal (Galp Energia)", "Ticker": "GALP.LS"},
    {"Setor": "E&P Petróleo e Gás", "Tipo": "Demais", "Empresa": "Repsol",                  "Ticker": "REP.MC"},

    # ============================================
    # 3) PETROQUÍMICA
    # ============================================
    {"Setor": "Petroquímica", "Tipo": "Estratégico", "Empresa": "Braskem", "Ticker": "BRKM5.SA"},

    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "Unipar",             "Ticker": "UNIP6.SA"},
    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "Oxiteno (Indorama)", "Ticker": "IVL.BK"},
    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "Dow",                "Ticker": "DOW"},
    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "BASF",               "Ticker": "BAS.DE"},
    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "Suzano",             "Ticker": "SUZB3.SA"},
    {"Setor": "Petroquímica", "Tipo": "Demais", "Empresa": "Alpek",              "Ticker": "ALPKF"},

    # ============================================
    # 4) DISTRIBUIÇÃO DE ENERGIA
    # ============================================
    {"Setor": "Distribuição de Energia", "Tipo": "Estratégico", "Empresa": "Coelba", "Ticker": "CEEB3.SA"},
    {"Setor": "Distribuição de Energia", "Tipo": "Demais",      "Empresa": "Eneva",  "Ticker": "ENEV3.SA"},
    {"Setor": "Distribuição de Energia", "Tipo": "Demais",      "Empresa": "Engie Brasil",  "Ticker": "EGIE3.SA"},
    {"Setor": "Distribuição de Energia", "Tipo": "Demais",      "Empresa": "Ômega Energia", "Ticker": "OMGE3.SA"},

    # ============================================
    # 5) LOGÍSTICA DE COMBUSTÍVEIS / TERMINAIS
    # ============================================
    {"Setor": "Logística de Combustíveis", "Tipo": "Demais", "Empresa": "Rumo",                "Ticker": "RAIL3.SA"},
    {"Setor": "Logística de Combustíveis", "Tipo": "Demais", "Empresa": "Hidrovias do Brasil", "Ticker": "HBSA3.SA"},
    {"Setor": "Logística de Combustíveis", "Tipo": "Demais", "Empresa": "Santos Brasil",       "Ticker": "STOSF"},
    {"Setor": "Logística de Combustíveis", "Tipo": "Demais", "Empresa": "Vopak",               "Ticker": "VPK.AS"},

    # ============================================
    # 6) GÁS / ENERGIA (INTERNACIONAL)
    # ============================================
    {"Setor": "Gás e Energia", "Tipo": "Demais", "Empresa": "New Fortress Energy", "Ticker": "NFE"},
]


def get_empresas_df() -> pd.DataFrame:
    """
    Retorna a base de empresas como DataFrame.
    """
    return pd.DataFrame(empresas)
