import factory

from app.security import hash_password
from models import Answer, Comment, Question, Tag, User
from tests.common import TestSession


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = TestSession
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    email = factory.Faker("email")
    password = factory.Faker("password")
    name = factory.Faker("name")

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        kwargs["password"] = hash_password(kwargs["password"])
        return super()._save(model_class, session, *args, **kwargs)

    class Meta:
        model = User


class TagFactory(BaseFactory):
    name = factory.Faker("word")

    class Meta:
        model = Tag


class QuestionFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")

    class Meta:
        model = Question


class AnswerFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    question = factory.SubFactory(QuestionFactory)
    user = factory.SubFactory(UserFactory)

    content = factory.Faker("paragraph")

    class Meta:
        model = Answer


class BaseCommentFactory(BaseFactory):
    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("paragraph")

    class Meta:
        abstract = True
        model = Comment


class QuestionCommentFactory(BaseCommentFactory):
    question = factory.SubFactory(QuestionFactory)


class AnwserCommentFactory(BaseCommentFactory):
    answer = factory.SubFactory(AnswerFactory)
