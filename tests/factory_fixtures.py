from pytest_factoryboy import register

from tests.factories import AnswerFactory, QuestionFactory, UserFactory

register(UserFactory)
register(UserFactory, "other_user")

register(QuestionFactory)
register(AnswerFactory)
