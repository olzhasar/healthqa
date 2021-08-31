from __future__ import annotations

from typing import TYPE_CHECKING

from storage import Store

if TYPE_CHECKING:
    from redis import Redis
    from sqlalchemy.orm.session import Session


class BaseRepostitory:
    store: Store

    def __init__(self, store: Store):
        self.store = store

    @property
    def db(self) -> Session:
        return self.store.db

    @property
    def redis(self) -> Redis:
        return self.store.redis

    def get(self, id: int):
        raise NotImplementedError

    def list(self, limit: int, offset: int):
        raise NotImplementedError
