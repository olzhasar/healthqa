import pytest
from pytest_factoryboy import LazyFixture

from tests import factories


@pytest.fixture
def question_with_related(user):
    question = factories.QuestionFactory()

    factories.VoteFactory.create_batch(2, entry_id=question.id)
    factories.VoteFactory(entry_id=question.id, user=user)

    for comment in factories.CommentFactory.create_batch(2, entry_id=question.id):
        factories.VoteFactory.create_batch(2, entry_id=comment.id)
        factories.VoteFactory(entry_id=comment.id, user=user)

    for answer in factories.AnswerFactory.create_batch(2, question=question):
        factories.VoteFactory.create_batch(2, entry_id=answer.id)
        factories.VoteFactory(entry_id=answer.id, user=user)

        for comment in factories.CommentFactory.create_batch(2, entry_id=answer.id):
            factories.VoteFactory.create_batch(2, entry_id=comment.id)
            factories.VoteFactory(entry_id=comment.id, user=user)

    return question


@pytest.fixture(
    params=[
        LazyFixture("question"),
        LazyFixture("answer"),
        LazyFixture("question_comment"),
        LazyFixture("answer_comment"),
    ]
)
def entry(request):
    return request.param.evaluate(request)


@pytest.fixture(
    params=[
        LazyFixture("question"),
        LazyFixture("answer"),
    ]
)
def question_or_answer(request):
    return request.param.evaluate(request)


@pytest.fixture(
    params=[
        LazyFixture("question_comment"),
        LazyFixture("answer_comment"),
    ]
)
def question_or_answer_comment(request):
    return request.param.evaluate(request)
