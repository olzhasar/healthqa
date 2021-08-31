from redis import Redis

from app.config import settings


def create_redis() -> Redis:
    return Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_MAIN_DB
    )
