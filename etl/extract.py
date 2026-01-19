import pandas as pd
import numpy as np
import yfinance as yf


def get_balance_sheet_all_yf(ticker_str: str) -> dict:
    tk = yf.Ticker(ticker_str)

    try:
        info = tk.info or {}
    except Exception:
        info = {}

    data = {
        "Fonte": "yfinance",
        "Preco Atual": info.get("currentPrice", np.nan),
        "Market Cap": info.get("marketCap", np.nan),
        "Setor": info.get("sector", ""),
        "Subsetor": info.get("industry", ""),
    }

    try:
        bs = tk.balance_sheet
    except Exception:
        bs = pd.DataFrame()

    if isinstance(bs, pd.DataFrame) and not bs.empty:
        col = bs.columns[0]
        serie = bs[col]

        for raw_idx, value in serie.items():
            nome_conta_raw = str(raw_idx).strip()
            col_name = (
                "BS_" +
                nome_conta_raw.replace(" ", "_")
                              .replace("/", "_")
                              .replace("-", "_")
                              .replace("(", "")
                              .replace(")", "")
            )
            data[col_name] = value
    else:
        data["Erro_balance_sheet"] = "Sem dados"

    return data


def extract_empresas(empresas_df: pd.DataFrame) -> pd.DataFrame:
    linhas = []

    for _, row in empresas_df.iterrows():
        empresa = row["Empresa"]
        ticker  = row["Ticker"]

        print(f"Extraindo {empresa} ({ticker})...")
        linha = {"Empresa": empresa, "Ticker": ticker}

        if isinstance(ticker, str) and ticker.strip():
            try:
                linha.update(get_balance_sheet_all_yf(ticker))
            except Exception as e:
                linha["Erro_yfinance"] = str(e)
        else:
            linha["Erro_yfinance"] = "Ticker inválido"

        linhas.append(linha)

    return pd.DataFrame(linhas)
