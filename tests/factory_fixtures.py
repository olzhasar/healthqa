from pytest_factoryboy import register

from tests.factories import UserFactory

register(UserFactory)
register(UserFactory, "other_user")
