from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from models import Base

if TYPE_CHECKING:
    from common.pagination import Paginator


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepostitory:
    """
    Class for isolating data sources activities
    """

    def get(self, id: int) -> ModelType:
        raise NotImplementedError

    def list(self, page: int, per_page: int) -> Paginator[ModelType]:
        raise NotImplementedError
