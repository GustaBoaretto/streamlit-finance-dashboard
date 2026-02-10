from repository.financial_repository import fetch_financials


def get_sector_snapshot(setor):

    df = fetch_financials(setor=setor)

    if df.empty:
        return df

    latest_date = df["data_referencia"].max()

    return df[df["data_referencia"] == latest_date]


def get_company_timeseries(ticker):

    df = fetch_financials(ticker=ticker)

    return df.sort_values("data_referencia")


def get_top_companies_by_roe(setor):

    df = get_sector_snapshot(setor)

    return df.sort_values("roe", ascending=False).head(10)
