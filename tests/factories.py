import factory
from factory.alchemy import SQLAlchemyModelFactory as BaseFactory

from app.security import hash_password
from models import Answer, Comment, Question, Tag, User
from tests.common import TestSession


class UserFactory(BaseFactory):
    email = factory.Faker("email")
    password = factory.Faker("password")
    name = factory.Faker("name")

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        kwargs["password"] = hash_password(kwargs["password"])
        return super()._save(model_class, session, *args, **kwargs)

    class Meta:
        model = User
        sqlalchemy_session = TestSession


class TagFactory(BaseFactory):
    name = factory.Faker("word")

    class Meta:
        model = Tag
        sqlalchemy_session = TestSession


class QuestionFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")

    class Meta:
        model = Question
        sqlalchemy_session = TestSession


class AnswerFactory(BaseFactory):
    question = factory.SubFactory(QuestionFactory)
    user = factory.SubFactory(UserFactory)

    content = factory.Faker("paragraph")

    class Meta:
        model = Answer
        sqlalchemy_session = TestSession


class BaseCommentFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("paragraph")

    class Meta:
        abstract = True
        model = Comment
        sqlalchemy_session = TestSession


class QuestionCommentFactory(BaseCommentFactory):
    question = factory.SubFactory(QuestionFactory)


class AnwserCommentFactory(BaseCommentFactory):
    answer = factory.SubFactory(AnswerFactory)
