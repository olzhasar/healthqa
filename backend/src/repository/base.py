from typing import Any, Generic, List, Optional, TypeVar, get_args

from sqlalchemy import exc
from sqlalchemy.orm.query import Query

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

    def _get(self, store, query: Query) -> ModelType:
        try:
            return query.one()
        except exc.NoResultFound:
            raise exceptions.NotFoundError

    def get(
        self,
        store: Store,
        id: int,
    ) -> ModelType:

        query = store.db.query(self.model).filter(self.model.id == id)
        return self._get(store, query)

    def first(self, store: Store) -> ModelType:
        return store.db.query(self.model).first()

    def exists(self, store: Store, id: Optional[int] = None) -> bool:
        query = store.db.query(self.model.id)
        if id:
            query = query.filter(self.model.id == id)

        return bool(query.first())

    def count(self, store: Store, *, filters: List[Any]):
        filters = filters or []
        return store.db.query(self.model.id).filter(*filters).count()

    def _list_default_filters(self) -> List[Any]:
        """Specify default filters that will be applied to list items"""
        return []

    def _list_default_ordering(self) -> List[Any]:
        """Specify clauses that will be used to order list items"""
        return []

    def _list_base_query(self, store: Store) -> Query:
        """Base query to use when retrieveing multiple instances"""
        return store.db.query(self.model)

    def all(
        self,
        store: Store,
        *,
        limit: int = 16,
        offset: int = 0,
        order_by: List[Any] = None,
        filters: List[Any] = None
    ):
        order_by = order_by or self._list_default_ordering()

        filters = filters or self._list_default_filters()
        query = self._list_base_query(store)

        return (
            query.filter(*filters).order_by(*order_by).limit(limit).offset(offset).all()
        )

    def list(
        self, store: Store, *, page: int, per_page: int, filters: List[Any] = None
    ) -> Paginator[ModelType]:
        filters = filters or []
        filters.extend(self._list_default_filters())

        total = self.count(store, filters=filters)
        offset = Paginator.calc_offset(page, per_page)

        objects = self.all(store, limit=per_page, offset=offset, filters=filters)

        return Paginator(objects=objects, total=total, page=page, per_page=per_page)
