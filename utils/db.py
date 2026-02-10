import pandas as pd
import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

# carrega .env local
load_dotenv()

# -------------------------
# secret router
# -------------------------
def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

# -------------------------
# conexão supabase
# -------------------------
@st.cache_resource
def get_supabase():
    return create_client(
        get_secret("SUPABASE_URL"),
        get_secret("SUPABASE_SERVICE_KEY")
    )

# -------------------------
# dados financeiros
# -------------------------
@st.cache_data(ttl=3600)
def loadfinancials(setor=None, empresa=None):

    supabase = get_supabase()

    query = supabase.table("vw_financials_enriched").select("*")

    if setor:
        query = query.eq("setor", setor)

    if empresa:
        query = query.eq("empresa", empresa)

    data = query.execute().data

    return pd.DataFrame(data)
