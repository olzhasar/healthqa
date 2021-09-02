import pytest

from auth.security import check_password
from repository import exceptions
from repository.user import UserRepository
from tests.factories import UserFactory

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


class TestList:
    @pytest.fixture
    def users(self):
        return UserFactory.create_batch(4)

    @pytest.mark.parametrize(
        ("page", "per_page", "n_pages", "exp_slice"),
        [
            (1, 4, 1, (0, 4)),
            (1, 2, 2, (0, 2)),
            (2, 2, 2, (2, 4)),
            (1, 3, 2, (0, 3)),
        ],
    )
    def test_page(
        self, users, repository: UserRepository, page, per_page, n_pages, exp_slice
    ):
        paginator = repository.list(page=page, per_page=per_page)

        assert paginator.objects == users[slice(*exp_slice)]
        assert paginator.total == len(users)
        assert paginator.page == page
        assert paginator.per_page == per_page
        assert len(paginator) == n_pages


class TestCreate:
    @pytest.fixture
    def data(self):
        return {
            "email": "info@test.com",
            "name": "Test User",
            "password": "123qweasd",
        }

    def test_ok(self, repository: UserRepository, data):
        user = repository.create(**data)

        from_db = repository.get(user.id)
        assert from_db == user
        assert from_db.email == data["email"]
        assert from_db.name == data["name"]
        assert check_password(data["password"], from_db.password)
