from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn, Optional, TypeVar

from models import Base
from storage import Store
from storage import store as main_store

if TYPE_CHECKING:
    from redis import Redis
    from sqlalchemy.orm.session import Session

    from common.pagination import Paginator


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepostitory:
    store: Store

    def __init__(self, store: Optional[Store] = None) -> NoReturn:
        self.store = store or main_store

    @property
    def db(self) -> Session:
        return self.store.db

    @property
    def redis(self) -> Redis:
        return self.store.redis

    def refresh(self, *instances: ModelType):
        for instance in instances:
            self.db.refresh(instance)

    def get(self, id: int) -> ModelType:
        raise NotImplementedError

    def list(self, limit: int, offset: int) -> Paginator[ModelType]:
        raise NotImplementedError
