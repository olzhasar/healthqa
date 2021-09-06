import meilisearch

from app.config import settings


def create_meili() -> meilisearch.Client:
    url = f"http://{settings.MEILI_HOST}:{settings.MEILI_PORT}"

    return meilisearch.Client(url, apiKey=settings.MEILI_API_KEY)
