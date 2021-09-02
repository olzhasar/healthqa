import pytest

from auth.security import check_password
from repository import exceptions
from repository.user import UserRepository
from tests.factories import UserFactory

pytestmark = pytest.mark.allow_db


@pytest.fixture
def repo(store):
    return UserRepository(store=store)


@pytest.fixture
def users(repo):
    return UserFactory.create_batch(4)


def test_get(repo: UserRepository, user):
    assert repo.get(user.id) == user


def test_non_existing(repo: UserRepository):
    with pytest.raises(exceptions.NotFoundError):
        repo.get(999)


def test_get_by_email(repo: UserRepository, user):
    assert repo.get_by_email(user.email) == user


def test_get_by_email_non_existing(repo: UserRepository):
    with pytest.raises(exceptions.NotFoundError):
        repo.get_by_email("non@existing.com")


@pytest.mark.parametrize(
    ("page", "per_page", "n_pages", "exp_slice"),
    [
        (1, 4, 1, (0, 4)),
        (1, 2, 2, (0, 2)),
        (2, 2, 2, (2, 4)),
        (1, 3, 2, (0, 3)),
    ],
)
def test_page(users, repo: UserRepository, page, per_page, n_pages, exp_slice):
    paginator = repo.list(page=page, per_page=per_page)

    assert paginator.objects == users[slice(*exp_slice)]
    assert paginator.total == len(users)
    assert paginator.page == page
    assert paginator.per_page == per_page
    assert len(paginator) == n_pages


@pytest.fixture
def data():
    return {
        "email": "info@test.com",
        "name": "Test User",
        "password": "123qweasd",
    }


def test_create(repo: UserRepository, data):
    user = repo.create(**data)

    from_db = repo.get(user.id)
    assert from_db == user
    assert from_db.email == data["email"]
    assert from_db.name == data["name"]
    assert check_password(data["password"], from_db.password)


def test_create_already_exists(repo: UserRepository, user, data):
    data["email"] = user.email

    with pytest.raises(exceptions.AlreadyExistsError):
        user = repo.create(**data)


def test_change_password(repo: UserRepository, user):
    repo.change_password(user, "new_password")

    assert check_password("new_password", user.password)

    from_db = repo.get(user.id)
    assert check_password("new_password", from_db.password)


def test_reset_password(repo: UserRepository, user):
    repo.reset_password(user)
    assert user.password is None

    from_db = repo.get(user.id)
    assert from_db.password is None


def test_update_info(repo: UserRepository, user):
    repo.update_info(user, name="New name")

    from_db = repo.get(user.id)
    assert user.name == from_db.name == "New name"


@pytest.mark.parametrize("user__email_verified", [False])
def test_mark_email_verified(repo: UserRepository, user):
    assert not user.email_verified

    repo.mark_email_verified(user)

    from_db = repo.get(user.id)
    assert user.email_verified is from_db.email_verified is True
