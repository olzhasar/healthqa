import factory

from models.user import User
from tests.common import TestSession


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    email = factory.Faker("email")
    username = factory.Faker("first_name")
    password = factory.Faker("password")

    class Meta:
        model = User
        sqlalchemy_session = TestSession
