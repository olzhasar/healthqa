from typing import cast

from flask import g
from redis import Redis
from sqlalchemy.orm.session import Session
from werkzeug.local import LocalProxy

from storage.db import create_session
from storage.redis import create_redis


class Store:
    _db: Session
    _redis_db: Redis

    def teardown(self):
        pass

    @property
    def db(self) -> Session:
        if not hasattr(self, "_db"):
            self._db = create_session()
        return self._db

    @property
    def redis(self) -> Redis:
        if not hasattr(self, "_redis"):
            self._redis = create_redis()
        return self._redis


def get_store() -> Store:
    if not hasattr(g, "_storage"):
        g._storage = Store()
    return g._storage


_store = LocalProxy(get_store)
store = cast(Store, _store)
