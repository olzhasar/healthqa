from redis import Redis

from app.config import settings

redis_db = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_MAIN_DB
)
