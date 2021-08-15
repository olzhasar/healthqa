import pytest
from sqlalchemy.orm.session import Session

import crud
from tests import factories


@pytest.fixture
def tags():
    return factories.TagFactory.create_batch(5)


def test_get_list(db: Session, tags, max_num_queries):
    with max_num_queries(1):
        result = crud.tag.get_list(db)

    assert result == tags


def test_get_choices(db: Session, tags, max_num_queries):
    with max_num_queries(1):
        result = crud.tag.get_choices(db)

    assert result == [(t.id, t.name) for t in tags]
