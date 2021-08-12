import pytest
from pytest_factoryboy import LazyFixture
from sqlalchemy.orm.session import Session

import crud
from models.entry import Entry
from tests import factories


class TestGetWithUserVote:
    @pytest.fixture(
        params=[
            LazyFixture("question"),
            LazyFixture("answer"),
            LazyFixture("question_comment"),
            LazyFixture("answer_comment"),
        ]
    )
    def instance(self, request):
        return request.param.evaluate(request)

    def test_ok(self, db: Session, instance, user, max_num_queries):
        factories.VoteFactory.create_batch(2, entry_id=instance.id)
        user_vote = factories.VoteFactory(entry_id=instance.id, user=user)

        with max_num_queries(1):
            entry = crud.entry.get_with_user_vote(db, id=instance.id, user_id=user.id)

            assert isinstance(entry, Entry)
            assert entry.user_vote == user_vote

    def test_no_user_vote(self, db: Session, instance, user, max_num_queries):
        factories.VoteFactory.create_batch(2, entry_id=instance.id)

        entry = crud.entry.get_with_user_vote(db, id=instance.id, user_id=user.id)

        assert isinstance(entry, Entry)
        assert not entry.user_vote
