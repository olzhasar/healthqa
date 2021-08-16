from datetime import datetime

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

import crud
from models.entry import Entry
from tests import factories


def test_get_with_user_vote(db: Session, entry, user, max_num_queries):
    factories.VoteFactory.create_batch(2, entry_id=entry.id)
    user_vote = factories.VoteFactory(entry_id=entry.id, user=user)

    with max_num_queries(1):
        entry = crud.entry.get_with_user_vote(db, id=entry.id, user_id=user.id)

        assert isinstance(entry, Entry)
        assert entry.user_vote == user_vote


def test_get_with_user_votes_no_vote(db: Session, entry, user, max_num_queries):
    factories.VoteFactory.create_batch(2, entry_id=entry.id)

    entry = crud.entry.get_with_user_vote(db, id=entry.id, user_id=user.id)

    assert isinstance(entry, Entry)
    assert not entry.user_vote


@pytest.mark.freeze_time("2030-01-01")
def test_mark_as_deleted(db: Session, entry, user):
    assert not entry.deleted_at

    crud.entry.mark_as_deleted(db, id=entry.id, user_id=user.id)

    db.refresh(entry)
    assert entry.deleted_at == datetime(2030, 1, 1)


def test_mark_as_deleted_not_found(db: Session, user):
    with pytest.raises(NoResultFound):
        crud.entry.mark_as_deleted(db, id=999, user_id=user.id)


def test_mark_as_deleted_wrong_user(db: Session, entry, other_user):
    with pytest.raises(NoResultFound):
        crud.entry.mark_as_deleted(db, id=entry.id, user_id=other_user.id)
