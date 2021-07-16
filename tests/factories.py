import factory

from app.security import hash_password
from models.user import User
from tests.common import TestSession


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    email = factory.Faker("email")
    username = factory.Faker("first_name")
    password = factory.Faker("password")

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        kwargs["password"] = hash_password(kwargs["password"])
        return super()._save(model_class, session, *args, **kwargs)

    class Meta:
        model = User
        sqlalchemy_session = TestSession
