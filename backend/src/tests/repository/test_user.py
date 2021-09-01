import pytest

from repository import exceptions
from repository.user import UserRepository

pytestmark = pytest.mark.allow_db


@pytest.fixture
def repository(store):
    return UserRepository(store=store)


class TestGet:
    def test_get(self, repository: UserRepository, user):
        assert repository.get(user.id) == user

    def test_non_existing(self, repository: UserRepository):
        with pytest.raises(exceptions.NotFoundError):
            repository.get(999)


class TestGetByEmail:
    def test_get(self, repository: UserRepository, user):
        assert repository.get_by_email(user.email) == user

    def test_non_existing(self, repository: UserRepository):
        with pytest.raises(exceptions.NotFoundError):
            repository.get_by_email("non@existing.com")
