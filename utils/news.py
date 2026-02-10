import feedparser
from urllib.parse import quote


def get_news(query: str, limit: int = 20):
    """
    Busca notícias no Google News RSS.
    """
    query_encoded = quote(query)
    url = f"https://news.google.com/rss/search?q={query_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    feed = feedparser.parse(url)

    noticias = []

    for entry in feed.entries[:limit]:
        noticias.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "source": entry.get("source", {}).get("title", ""),
            "summary": entry.get("description", "")
        })

    return noticias
