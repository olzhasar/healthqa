from typing import Any, Generic, List, TypeVar, get_args

from common.pagination import Paginator
from models import Base
from repository import exceptions
from storage import Store

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepostitory(Generic[ModelType]):
    """
    Class for isolating data sources activities
    """

    @classmethod
    @property
    def model(cls) -> ModelType:
        """
        Retrieve ModelType specified in Generic
        """
        return get_args(cls.__orig_bases__[0])[0]

    def get(
        self,
        store: Store,
        id: int,
        *,
        options: List[Any] = None,
        filters: List[Any] = None
    ) -> ModelType:

        options = options or []
        filters = filters or []

        instance = store.db.query(self.model).options(*options).filter(*filters).get(id)
        if instance is None:
            raise exceptions.NotFoundError

        return instance

    def _get_default_filters(self) -> List[Any]:
        return []

    def count(self, store: Store, *, filters: List[Any]):
        filters = filters or []
        return store.db.query(self.model.id).filter(*filters).count()

    def all(
        self,
        store: Store,
        *,
        limit: int = 16,
        offset: int = 0,
        filters: list[Any] = None
    ):
        filters = filters or self._get_default_filters()

        return (
            store.db.query(self.model).filter(*filters).limit(limit).offset(offset).all()
        )

    def list(
        self, store: Store, *, page: int, per_page: int, filters: List[Any] = None
    ) -> Paginator[ModelType]:
        filters = filters or []
        filters.extend(self._get_default_filters())

        total = self.count(store, filters=filters)
        offset = Paginator.calc_offset(page, per_page)

        objects = self.all(store, limit=per_page, offset=offset, filters=filters)

        return Paginator(objects=objects, total=total, page=page, per_page=per_page)
