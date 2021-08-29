from typing import cast

from flask import g
from redis import Redis
from werkzeug.local import LocalProxy

from app.config import settings


def get_redis_db():
    if not hasattr(g, "_redis"):
        g._redis = Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_MAIN_DB
        )
    return g._redis


_redis_db = LocalProxy(get_redis_db)
redis_db = cast(Redis, _redis_db)
