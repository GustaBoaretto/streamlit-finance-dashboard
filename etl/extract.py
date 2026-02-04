import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime


# =====================================================
# Extrai histórico COMPLETO de Balanço + DRE (RAW)
# =====================================================
def extract_fundamentals_history_yf(
    ticker_str: str,
    max_periods: int = 12   # 12 períodos (trimestres ou anos, conforme Yahoo)
) -> pd.DataFrame:
    """
    Extrai histórico completo de Balanço Patrimonial + DRE do Yahoo Finance.
    Retorna uma linha por Ticker + Data_Referencia.
    """

    tk = yf.Ticker(ticker_str)

    # -----------------------------
    # Data da coleta (snapshot)
    # -----------------------------
    data_consulta = datetime.now().date()

    # -----------------------------
    # Download dos dados
    # -----------------------------
    try:
        bs = tk.balance_sheet
    except Exception:
        bs = pd.DataFrame()

    try:
        is_ = tk.financials
    except Exception:
        is_ = pd.DataFrame()

    if bs.empty and is_.empty:
        print(f"⚠️ Sem dados contábeis para {ticker_str}")
        return pd.DataFrame()

    # -----------------------------
    # Lista unificada de períodos
    # -----------------------------
    periods = set()

    if not bs.empty:
        periods.update(bs.columns.tolist())

    if not is_.empty:
        periods.update(is_.columns.tolist())

    periods = sorted(periods, reverse=True)[:max_periods]

    rows = []

    # -----------------------------
    # Constrói linhas (1 por período)
    # -----------------------------
    for period in periods:
        row = {
            "Ticker": ticker_str,
            "Data_Referencia": pd.to_datetime(period),
            "data_consulta": data_consulta
        }

        # -------- BALANÇO --------
        if not bs.empty and period in bs.columns:
            for account, value in bs[period].items():
                col_name = (
                    "BS_" +
                    str(account)
                    .strip()
                    .replace(" ", "_")
                    .replace("/", "_")
                    .replace("-", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                row[col_name] = value

        # -------- DRE --------
        if not is_.empty and period in is_.columns:
            for account, value in is_[period].items():
                col_name = (
                    "IS_" +
                    str(account)
                    .strip()
                    .replace(" ", "_")
                    .replace("/", "_")
                    .replace("-", "_")
                    .replace("(", "")
                    .replace(")", "")
                )
                row[col_name] = value

        rows.append(row)

    return pd.DataFrame(rows)


# =====================================================
# Extrai dados para múltiplas empresas
# =====================================================
def extract_empresas(empresas_df: pd.DataFrame) -> pd.DataFrame:
    """
    empresas_df deve conter:
    - Empresa
    - Ticker
    """

    frames = []

    for _, row in empresas_df.iterrows():
        empresa = row["Empresa"]
        ticker = row["Ticker"]

        print(f"📥 Extraindo {empresa} ({ticker})...")

        if not isinstance(ticker, str) or not ticker.strip():
            print(f"⚠️ Ticker inválido: {empresa}")
            continue

        try:
            df = extract_fundamentals_history_yf(
                ticker_str=ticker.strip(),
                max_periods=12
            )

            if df.empty:
                continue

            df["Empresa"] = empresa
            frames.append(df)

        except Exception as e:
            print(f"❌ Erro em {ticker}: {e}")

    if not frames:
        print("⚠️ Nenhum dado extraído")
        return pd.DataFrame()

    df_final = pd.concat(frames, ignore_index=True)

    print(f"✅ Extração finalizada: {len(df_final)} linhas")

    return df_final


