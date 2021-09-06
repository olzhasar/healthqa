from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import meilisearch
from flask import g

from storage.db import create_session
from storage.meili import create_meili
from storage.redis import create_redis

if TYPE_CHECKING:
    from redis import Redis
    from sqlalchemy.orm.session import Session


class Store:
    """Class to serve as a single access point to all data sources"""

    _db: Optional[Session]
    _redis_db: Optional[Redis]
    _meili: Optional[meilisearch.Client]

    def __init__(
        self, db: Session = None, redis: Redis = None, meili: meilisearch.Client = None
    ):
        self._db = db
        self._redis = redis
        self._meili = meili

    def teardown(self) -> None:
        """
        Close all connections
        """

        if self._db is not None:
            self._db.close()

        if self._redis is not None:
            self._redis.close()

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = create_session()
        return self._db

    @property
    def redis(self) -> Redis:
        if self._redis is None:
            self._redis = create_redis()
        return self._redis

    @property
    def meili(self) -> meilisearch.Client:
        if not self._meili:
            self._meili = create_meili()
        return self._meili

    def refresh(self, instance: Any, *args: Any, **kwargs: Any) -> None:
        return self.db.refresh(instance, *args, **kwargs)


def get_store() -> Store:
    if not hasattr(g, "_store"):
        g._store = Store()
    return g._store
