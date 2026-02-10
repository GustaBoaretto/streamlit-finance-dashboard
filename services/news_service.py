from utils.news import get_news
from utils.llm import summarize_news


def get_sector_news(setor):

    news = get_news(setor, limit=10)

    for n in news:
        text = f"{n['title']} {n['summary']}"
        n["llm_summary"] = summarize_news(text, setor)

    return news
