from pytest_factoryboy import LazyFixture, register

from tests import factories

register(factories.UserFactory)
register(factories.UserFactory, "other_user")

register(factories.QuestionFactory)
register(factories.AnswerFactory)

register(
    factories.CommentFactory,
    "question_comment",
    user_action_id=LazyFixture(lambda question: question.id),
)
register(
    factories.CommentFactory,
    "answer_comment",
    user_action_id=LazyFixture(lambda answer: answer.id),
)

register(factories.TagFactory)
register(factories.TagFactory, "other_tag")
