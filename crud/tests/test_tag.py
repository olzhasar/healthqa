import pytest
from sqlalchemy.orm.session import Session

import crud
from tests import factories


@pytest.fixture
def tags():
    return factories.TagFactory.create_batch(5)


@pytest.fixture
def categories():
    categories = factories.TagCategoryFactory.create_batch(3)
    for category in categories:
        factories.TagFactory.create_batch(2, category=category)

    return categories


def test_get_list(db: Session, tags, max_num_queries):
    with max_num_queries(1):
        result = crud.tag.get_list(db)

    assert result == tags


def test_get_choices(db: Session, tags, max_num_queries):
    with max_num_queries(1):
        result = crud.tag.get_choices(db)

    assert result == [(t.id, t.name) for t in tags]


def test_get_categories_list(db: Session, categories, max_num_queries):
    with max_num_queries(1):
        result = crud.tag.get_categories_list(db)

        for category in result:
            assert len(category.tags) == 2
            for tag in category.tags:
                tag.id

    assert set(result) == set(categories)
