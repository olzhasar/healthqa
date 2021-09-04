from flask import Flask

import repository as repo
from storage import store


class TagCategoriesLazy:
    def __init__(self):
        self._tag_categories = None

    def __iter__(self):
        if not self._tag_categories:
            self._tag_categories = repo.tag_category.all(store)

        for category in self._tag_categories:
            yield category


def tags_context_processor():
    return dict(tag_categories=TagCategoriesLazy())


def init_app(app: Flask):
    app.context_processor(tags_context_processor)
