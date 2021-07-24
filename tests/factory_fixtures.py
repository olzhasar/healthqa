from pytest_factoryboy import register

from tests.factories import AnswerFactory, QuestionFactory, TagFactory, UserFactory

register(UserFactory)
register(UserFactory, "other_user")

register(QuestionFactory)
register(AnswerFactory)

register(TagFactory)
register(TagFactory, "other_tag")
