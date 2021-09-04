from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import exc
from sqlalchemy.orm import joinedload

from models import Tag, TagCategory
from repository import exceptions
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class TagCategoryRepository(BaseRepostitory[TagCategory]):
    def all(self, store: Store) -> list[TagCategory]:
        return store.db.query(TagCategory).options(joinedload(TagCategory.tags)).all()


class TagRepository(BaseRepostitory[Tag]):
    def get_by_slug(self, store: Store, slug: str) -> Tag:
        try:
            return store.db.query(Tag).filter(Tag.slug == slug).one()
        except exc.NoResultFound:
            raise exceptions.NotFoundError


tag_category = TagCategoryRepository()
tag = TagRepository()
