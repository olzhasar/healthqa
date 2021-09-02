from typing import Generic, TypeVar

from models import Base

ModelType = TypeVar("ModelType", bound=Base)


class Paginator(Generic[ModelType]):
    _objects: list[ModelType]
    total: int
    current: int
    n_pages: int

    def __init__(
        self, *, objects: list[ModelType], total: int, page: int, per_page: int
    ):
        self.objects = objects
        self.total = total
        self.page = max(page, 1)
        self.per_page = per_page
        self.n_pages = (total - 1) // per_page + 1

    @staticmethod
    def calc_offset(page: int, per_page):
        return per_page * (page - 1)

    def __len__(self):
        return self.n_pages

    @property
    def has_next(self) -> bool:
        return self.page < self.n_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def page_range(self):
        low = max(1, self.page - 4)
        high = min(self.n_pages + 1, self.page + 5)

        return range(low, high)

    def __bool__(self) -> bool:
        return self.n_pages > 1
