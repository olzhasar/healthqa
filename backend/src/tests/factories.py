import factory
import factory.fuzzy

from models import Answer, Comment, Question, Tag, TagCategory, User, Vote
from tests.session import TestSession


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = TestSession
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.Faker("password")
    name = factory.Faker("name")

    email_verified = True

    class Meta:
        model = User


class TagCategoryFactory(BaseFactory):
    name = factory.Faker("word")

    class Meta:
        model = TagCategory
        sqlalchemy_get_or_create = ("name",)


class TagFactory(BaseFactory):
    name = factory.Faker("word")
    slug = factory.SelfAttribute("name")
    category = factory.SubFactory(TagCategoryFactory)

    class Meta:
        model = Tag
        sqlalchemy_get_or_create = ("name",)


class QuestionFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)

    title = factory.Faker("sentence")
    slug = factory.Faker("slug")
    content = factory.Faker("paragraph")

    score = 0

    class Meta:
        model = Question


class AnswerFactory(BaseFactory):
    question = factory.SubFactory(QuestionFactory)
    user = factory.SubFactory(UserFactory)

    content = factory.Faker("paragraph")

    score = 0

    class Meta:
        model = Answer


class CommentFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)
    content = factory.Faker("paragraph")
    entry_id = None

    class Meta:
        model = Comment


class VoteFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)
    entry_id = None
    value = factory.fuzzy.FuzzyChoice([-1, 1])

    class Meta:
        model = Vote
