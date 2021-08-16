import pytest
from sqlalchemy.orm.session import Session

import crud
from models import Vote
from tests import factories


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_new(db: Session, entry, user, input_val, value):
    vote = crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=input_val)

    from_db = (
        db.query(Vote).filter(Vote.entry_id == entry.id, Vote.user_id == user.id).one()
    )

    assert from_db == vote
    assert from_db.value == value


@pytest.mark.parametrize("input_val", [-1, 3, 4, 99])
def test_register_invalid_value(db: Session, entry, user, input_val):
    with pytest.raises(ValueError) as exc:
        crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=input_val)
        assert str(exc) == "Invalid vote value"

    assert not bool(
        db.query(Vote.id)
        .filter(Vote.entry_id == entry.id, Vote.user_id == user.id)
        .first()
    )


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_same_value(db: Session, entry, user, input_val, value):
    factories.VoteFactory(entry_id=entry.id, user=user, value=value)

    with pytest.raises(ValueError) as exc:
        crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=input_val)
        assert str(exc) == "Vote already exists"


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_different_value(db: Session, entry, user, input_val, value):
    vote = factories.VoteFactory(entry_id=entry.id, user=user, value=-value)

    crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=input_val)

    db.refresh(vote)
    assert vote.value == value


def test_register_delete(db: Session, entry, user):
    factories.VoteFactory(entry_id=entry.id, user=user, value=1)

    crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=0)

    assert not bool(
        db.query(Vote.id)
        .filter(Vote.entry_id == entry.id, Vote.user_id == user.id)
        .first()
    )


def test_register_delete_not_existing(db: Session, entry, user):
    with pytest.raises(ValueError) as exc:
        crud.vote.record(db, user_id=user.id, entry_id=entry.id, value=0)
        assert str(exc) == "Vote does not exist"


def test_score_calculation(db: Session, entry, question, user):
    another_entry = factories.QuestionFactory(user=user)

    factories.VoteFactory.create_batch(5, entry_id=entry.id, value=1)

    db.refresh(entry)
    db.refresh(user)

    assert entry.score == user.score == 5

    factories.VoteFactory.create_batch(3, entry_id=another_entry.id, value=1)

    db.refresh(entry)
    db.refresh(another_entry)
    db.refresh(user)

    assert entry.score == 5
    assert another_entry.score == 3
    assert user.score == 8
