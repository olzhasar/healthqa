import pytest
from pytest_factoryboy import LazyFixture

import crud
from models import Entry, Vote
from tests import factories


def test_get_dict_for_user(db, user):
    expected = {}

    for question in factories.QuestionFactory.create_batch(3):
        vote = factories.VoteFactory(entry_id=question.id, user=user)
        expected[question.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=question.id)

    for answer in factories.AnswerFactory.create_batch(3):
        vote = factories.VoteFactory(entry_id=answer.id, user=user)
        expected[answer.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=answer.id)

    for comment in factories.CommentFactory.create_batch(3, entry_id=question.id):
        vote = factories.VoteFactory(entry_id=comment.id, user=user)
        expected[comment.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=comment.id)

    result = crud.vote.get_dict_for_user(db, user_id=user.id)
    assert result == expected


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


def test_delete(db, instance, user):
    factories.VoteFactory(user=user, entry_id=instance.id, value=5)

    assert db.query(Entry.score).filter(Entry.id == instance.id).scalar() == 5

    crud.vote.delete(db, user_id=user.id, entry_id=instance.id)

    assert not bool(
        db.query(Vote)
        .filter(Vote.user_id == user.id, Vote.entry_id == instance.id)
        .first()
    )
    assert db.query(Entry.score).filter(Entry.id == instance.id).scalar() == 0
