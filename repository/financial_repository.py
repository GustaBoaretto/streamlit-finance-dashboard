import pandas as pd
from utils.db import get_supabase


def fetch_financials(setor=None, empresa=None, ticker=None):

    supabase = get_supabase()

    query = supabase.table("vw_financials_enriched").select("*")

    if setor:
        query = query.eq("setor", setor)

    if empresa:
        query = query.eq("empresa", empresa)

    if ticker:
        query = query.eq("ticker", ticker)

    data = query.execute().data

    return pd.DataFrame(data)
