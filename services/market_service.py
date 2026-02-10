from utils.news import get_news
from utils.llm import summarize_news
from utils.db import load_financials

def get_market_news(query):

    news = get_news(query)

    for n in news:
        text = f"{n['title']} {n['summary']}"
        n["llm_summary"] = summarize_news(text)

    return news


def get_sector_snapshot(setor):
    return load_financials(setor=setor)
