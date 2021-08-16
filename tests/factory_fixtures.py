import pytest
from pytest_factoryboy import LazyFixture, register

from tests import factories

register(factories.UserFactory)
register(factories.UserFactory, "other_user")

register(factories.QuestionFactory)
register(factories.AnswerFactory)

register(
    factories.CommentFactory,
    "question_comment",
    entry_id=LazyFixture(lambda question: question.id),
)
register(
    factories.CommentFactory,
    "answer_comment",
    entry_id=LazyFixture(lambda answer: answer.id),
)

register(factories.TagFactory)
register(factories.TagFactory, "other_tag")


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
