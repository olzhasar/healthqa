from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Generator, List

from flask import Flask

import repository as repo
from storage import store

if TYPE_CHECKING:
    from models import TagCategory


class TagCategoriesLazy:
    def __init__(self) -> None:
        self._tag_categories: List[TagCategory] = []

    def __iter__(self) -> Generator:
        if not self._tag_categories:
            self._tag_categories = repo.tag_category.all(store)

        for category in self._tag_categories:
            yield category


def tags_context_processor() -> Dict[str, Any]:
    return dict(tag_categories=TagCategoriesLazy())


def init_app(app: Flask) -> None:
    app.context_processor(tags_context_processor)
