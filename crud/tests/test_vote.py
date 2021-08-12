import pytest
from pytest_factoryboy import LazyFixture
from sqlalchemy.orm.session import Session

import crud
from models import Vote
from tests import factories


@pytest.fixture(
    params=[
        LazyFixture("question"),
        LazyFixture("answer"),
        LazyFixture("question_comment"),
        LazyFixture("answer_comment"),
    ]
)
def instance(request):
    return request.param.evaluate(request)


class TestRegister:
    @pytest.mark.parametrize(
        ("input_val", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_new(self, db: Session, instance, user, input_val, value):
        vote = crud.vote.record(
            db, user_id=user.id, entry_id=instance.id, value=input_val
        )

        from_db = (
            db.query(Vote)
            .filter(Vote.entry_id == instance.id, Vote.user_id == user.id)
            .one()
        )

        assert from_db == vote
        assert from_db.value == value

    @pytest.mark.parametrize("input_val", [-1, 3, 4, 99])
    def test_invalid_value(self, db: Session, instance, user, input_val):
        with pytest.raises(ValueError) as exc:
            crud.vote.record(db, user_id=user.id, entry_id=instance.id, value=input_val)
            assert str(exc) == "Invalid vote value"

        assert not bool(
            db.query(Vote.id)
            .filter(Vote.entry_id == instance.id, Vote.user_id == user.id)
            .first()
        )

    @pytest.mark.parametrize(
        ("input_val", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_existing_same_value(self, db: Session, instance, user, input_val, value):
        factories.VoteFactory(entry_id=instance.id, user=user, value=value)

        with pytest.raises(ValueError) as exc:
            crud.vote.record(db, user_id=user.id, entry_id=instance.id, value=input_val)
            assert str(exc) == "Vote already exists"

    @pytest.mark.parametrize(
        ("input_val", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_existing_different_value(
        self, db: Session, instance, user, input_val, value
    ):
        vote = factories.VoteFactory(entry_id=instance.id, user=user, value=-value)

        crud.vote.record(db, user_id=user.id, entry_id=instance.id, value=input_val)

        db.refresh(vote)
        assert vote.value == value

    def test_delete(self, db: Session, instance, user):
        factories.VoteFactory(entry_id=instance.id, user=user, value=1)

        crud.vote.record(db, user_id=user.id, entry_id=instance.id, value=0)

        assert not bool(
            db.query(Vote.id)
            .filter(Vote.entry_id == instance.id, Vote.user_id == user.id)
            .first()
        )

    def test_delete_not_existing(self, db: Session, instance, user):
        with pytest.raises(ValueError) as exc:
            crud.vote.record(db, user_id=user.id, entry_id=instance.id, value=0)
            assert str(exc) == "Vote does not exist"
