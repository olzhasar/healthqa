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


def test_delete(db: Session, entry, user):
    crud.entry.delete(db, id=entry.id, user_id=user.id)

    assert not bool(db.query(Entry.id).filter(Entry.id == entry.id).first())


def test_delete_not_found(db: Session, user):
    with pytest.raises(NoResultFound):
        crud.entry.delete(db, id=999, user_id=user.id)


def test_delete_wrong_user(db: Session, entry, other_user):
    with pytest.raises(NoResultFound):
        crud.entry.delete(db, id=entry.id, user_id=other_user.id)
