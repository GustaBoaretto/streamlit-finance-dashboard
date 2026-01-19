import numpy as np
import pandas as pd
import yfinance as yf


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


def transform_financials(df: pd.DataFrame) -> pd.DataFrame:

    # =========================
    # Balanço
    # =========================
    df["Ativo Total"]        = df.get("BS_Total_Assets")
    df["Passivo Total"]      = df.get("BS_Total_Liabilities_Net_Minority_Interest")
    df["Patrimônio Líquido"] = df.get("BS_Stockholders_Equity")

    df["Ativo Circulante"]   = df.get("BS_Current_Assets")
    df["Passivo Circulante"] = df.get("BS_Current_Liabilities")

    df["Ativo Não Circulante"]   = df["Ativo Total"]   - df["Ativo Circulante"]
    df["Passivo Não Circulante"] = df["Passivo Total"] - df["Passivo Circulante"]

    df["Dívida Total"] = df.get("BS_Total_Debt")

    cash_cols = [
        "BS_Cash_Cash_Equivalents_And_Short_Term_Investments",
        "BS_Cash_And_Cash_Equivalents",
        "BS_Cash_Equivalents",
        "BS_Cash_Financial",
    ]

    df["Caixa Total"] = df[cash_cols].bfill(axis=1).iloc[:, 0]
    df["Dívida Líquida"] = df["Dívida Total"] - df["Caixa Total"]

    # =========================
    # DRE
    # =========================
    df["EBIT"] = np.nan
    df["EBITDA"] = np.nan
    df["EBITDA Ajustado"] = np.nan
    df["Receita Líquida"] = np.nan
    df["Despesa de Juros"] = np.nan
    df["Lucro Líquido"] = np.nan

    for i, row in df.iterrows():
        ticker = str(row.get("Ticker", "")).strip()
        if not ticker:
            continue

        try:
            t = yf.Ticker(ticker)
            fin = t.financials

            df.at[i, "EBIT"] = get_first_non_null_row(fin, ["EBIT", "Operating Income"])
            df.at[i, "EBITDA"] = get_first_non_null_row(fin, ["EBITDA"])
            df.at[i, "EBITDA Ajustado"] = get_first_non_null_row(fin, ["Normalized EBITDA"])
            df.at[i, "Receita Líquida"] = get_first_non_null_row(fin, ["Total Revenue", "Revenue"])
            df.at[i, "Despesa de Juros"] = get_first_non_null_row(fin, ["Interest Expense"])
            df.at[i, "Lucro Líquido"] = get_first_non_null_row(fin, ["Net Income"])

        except Exception as e:
            print(f"Erro no ticker {ticker}: {e}")

    # =========================
    # Indicadores
    # =========================
    ebitda_base = df["EBITDA Ajustado"].where(
        df["EBITDA Ajustado"].notna(),
        df["EBITDA"]
    )

    df["Liquidez Corrente"] = df["Ativo Circulante"] / df["Passivo Circulante"]
    df["ICJ"] = df["EBIT"] / df["Despesa de Juros"].abs()
    df["Dívida Líquida / EBITDA"] = df["Dívida Líquida"] / ebitda_base
    df["Endividamento"] = df["Dívida Total"] / df["Ativo Total"]
    df["Margem EBITDA"] = ebitda_base / df["Receita Líquida"]
    df["ROE"] = df["Lucro Líquido"] / df["Patrimônio Líquido"]

    return df