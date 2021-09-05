import pytest

import repository as repo
from repository import exceptions
from storage import Store
from tests import factories

pytestmark = [pytest.mark.allow_db]


@pytest.fixture
def tags():
    return factories.TagFactory.create_batch(5)


@pytest.fixture
def categories():
    categories = factories.TagCategoryFactory.create_batch(3)
    for category in categories:
        factories.TagFactory.create_batch(2, category=category)

    return categories


def test_get_by_slug(store: Store, tag, other_tag):
    assert repo.tag.get_by_slug(store, tag.slug) == tag
    assert repo.tag.get_by_slug(store, other_tag.slug) == other_tag


def test_get_by_slug_non_existing(store: Store):
    with pytest.raises(exceptions.NotFoundError):
        repo.tag.get_by_slug(store, "non_existing")


def test_get_categories_list(store: Store, categories, max_num_queries):
    with max_num_queries(1):
        result = repo.tag_category.all(store)

        for category in result:
            assert len(category.tags) == 2
            for tag in category.tags:
                tag.id

    assert set(result) == set(categories)
