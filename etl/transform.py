import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone


# ======================================================
# Utilitário
# ======================================================
def get_first_non_null_row(df_yf, row_names):
    if df_yf is None or df_yf.empty:
        return np.nan

    col = df_yf.columns[0]

    for name in row_names:
        if name in df_yf.index:
            val = df_yf.loc[name, col]
            if pd.notna(val):
                return val

    return np.nan


# ======================================================
# Transformação principal
# ======================================================
def transform_financials(df: pd.DataFrame) -> pd.DataFrame:

    print("Transformando indicadores financeiros...")

    df = df.copy()

    # ==================================================
    # NORMALIZAÇÃO DE COLUNAS BÁSICAS
    # ==================================================
    if "Ticker" in df.columns:
        df.rename(columns={"Ticker": "ticker"}, inplace=True)

    if "Data_Referencia" in df.columns:
        df.rename(columns={"Data_Referencia": "Data_Referencia"}, inplace=True)

    # ==================================================
    # PADRONIZAÇÃO DO BALANÇO
    # ==================================================
    BALANCE_MAP = {
        "BS_Total_Assets": "Ativo Total",
        "BS_Total_Liabilities_Net_Minority_Interest": "Passivo Total",
        "BS_Stockholders_Equity": "Patrimônio Líquido",
        "BS_Current_Assets": "Ativo Circulante",
        "BS_Current_Liabilities": "Passivo Circulante",
        "BS_Total_Debt": "Dívida Total",
    }

    for raw, final in BALANCE_MAP.items():
        if raw in df.columns:
            df[final] = df[raw]

    # ==================================================
    # CAIXA TOTAL (COALESCE SEGURO)
    # ==================================================
    CASH_COLS = [
        "BS_Cash_Cash_Equivalents_And_Short_Term_Investments",
        "BS_Cash_And_Cash_Equivalents",
        "BS_Cash_Equivalents",
        "BS_Cash_Financial",
    ]

    cash_existentes = [c for c in CASH_COLS if c in df.columns]

    if cash_existentes:
        df["Caixa Total"] = (
            df[cash_existentes]
            .bfill(axis=1)
            .iloc[:, 0]
        )
    else:
        df["Caixa Total"] = np.nan

    # ==================================================
    # DERIVADOS DO BALANÇO
    # ==================================================
    df["Ativo Não Circulante"] = df["Ativo Total"] - df["Ativo Circulante"]
    df["Passivo Não Circulante"] = df["Passivo Total"] - df["Passivo Circulante"]
    df["Dívida Líquida"] = df["Dívida Total"] - df["Caixa Total"]

    # ==================================================
    # DRE (CACHE POR TICKER)
    # ==================================================
    dre_cache = {}

    for ticker in df["ticker"].dropna().unique():

        ticker = str(ticker).strip()
        if not ticker:
            continue

        try:
            print(f"Baixando DRE: {ticker}")
            t = yf.Ticker(ticker)
            fin = t.financials

            dre_cache[ticker] = {
                "EBIT": get_first_non_null_row(fin, ["EBIT", "Operating Income"]),
                "EBITDA": get_first_non_null_row(fin, ["EBITDA"]),
                "EBITDA Ajustado": get_first_non_null_row(fin, ["Normalized EBITDA"]),
                "Receita Líquida": get_first_non_null_row(fin, ["Total Revenue", "Revenue"]),
                "Despesa de Juros": get_first_non_null_row(fin, ["Interest Expense"]),
                "Lucro Líquido": get_first_non_null_row(fin, ["Net Income"]),
            }

        except Exception as e:
            print(f"Erro no ticker {ticker}: {e}")
            dre_cache[ticker] = {}

    for col in [
        "EBIT",
        "EBITDA",
        "EBITDA Ajustado",
        "Receita Líquida",
        "Despesa de Juros",
        "Lucro Líquido",
    ]:
        df[col] = df["ticker"].map(
            lambda t: dre_cache.get(str(t).strip(), {}).get(col, np.nan)
        )

    # ==================================================
    # INDICADORES FINANCEIROS
    # ==================================================
    def safe_div(n, d):
        return np.where((d == 0) | pd.isna(d), np.nan, n / d)

    ebitda_base = df["EBITDA Ajustado"].where(
        df["EBITDA Ajustado"].notna(),
        df["EBITDA"]
    )

    df["Liquidez Corrente"] = safe_div(
        df["Ativo Circulante"],
        df["Passivo Circulante"]
    )

    df["ICJ"] = safe_div(
        df["EBIT"],
        df["Despesa de Juros"].abs()
    )

    df["ICJ Ajustado"] = safe_div(
        ebitda_base,
        df["Despesa de Juros"].abs()
    )

    df["Dívida Líquida / EBITDA"] = safe_div(
        df["Dívida Líquida"],
        df["EBITDA"]
    )

    df["Dívida Líquida / EBITDA Ajustado"] = safe_div(
        df["Dívida Líquida"],
        ebitda_base
    )

    df["Endividamento"] = safe_div(
        df["Dívida Total"],
        df["Ativo Total"]
    )

    df["Endividamento Ajustado"] = safe_div(
        df["Dívida Líquida"],
        df["Ativo Total"]
    )

    df["Margem EBITDA"] = safe_div(
        ebitda_base,
        df["Receita Líquida"]
    )

    df["ROE"] = safe_div(
        df["Lucro Líquido"],
        df["Patrimônio Líquido"]
    )

    df["ROE Ajustado"] = safe_div(
        df["Lucro Líquido"],
        df["Patrimônio Líquido"].abs()
    )
    
    # ==================================================
    # SELEÇÃO FINAL (PADRÃO DA SUA ETL)
    # ==================================================
    COLUNAS_FINAIS = [
        "Data_Referencia",
        "empresa",
        "ticker",

        "Liquidez Corrente",
        "ICJ",
        "ICJ Ajustado",
        "Dívida Líquida / EBITDA",
        "Dívida Líquida / EBITDA Ajustado",
        "Endividamento",
        "Endividamento Ajustado",
        "Margem EBITDA",
        "ROE",
        "ROE Ajustado",

        "Ativo Total",
        "Passivo Total",
        "Patrimônio Líquido",
        "Ativo Circulante",
        "Passivo Circulante",
        "Ativo Não Circulante",
        "Passivo Não Circulante",
        "Dívida Total",
        "Caixa Total",
        "Dívida Líquida",

        "EBIT",
        "EBITDA",
        "EBITDA Ajustado",
        "Receita Líquida",
        "Despesa de Juros",
        "Lucro Líquido",
    ]

    df = df[[c for c in COLUNAS_FINAIS if c in df.columns]]

    # ==================================================
    # PADRONIZAÇÃO FINAL: 2 CASAS DECIMAIS
    # ==================================================
    COLUNAS_NUMERICAS = df.select_dtypes(include=[np.number]).columns

    for col in COLUNAS_NUMERICAS:
        df[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .round(2)
        )
        
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    return df
