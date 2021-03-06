import random

import pytest
from sqlalchemy.orm.session import Session

import repository as repo
from auth.security import check_password
from models.answer import Answer
from models.question import Question
from repository import exceptions
from storage.base import Store
from tests import factories
from tests.factories import UserFactory

pytestmark = pytest.mark.allow_db


@pytest.fixture
def users():
    return UserFactory.create_batch(4)


def test_get(store: Store, user, max_num_queries):
    assert repo.user.get(store, user.id) == user


def test_get_non_existing(store: Store):
    with pytest.raises(exceptions.NotFoundError):
        repo.user.get(store, 999)


def test_first_with_passsword(store: Store, db: Session, user, max_num_queries):
    user_id = user.id
    user_password = user.password
    db.expire(user)

    with max_num_queries(1):
        assert repo.user.first_with_password(store, user_id).password == user_password


def test_first_with_passsword_non_existing(store: Store, db: Session):
    assert repo.user.first_with_password(store, 999) is None


def test_get_by_email(store: Store, user, max_num_queries):
    with max_num_queries(1):
        assert repo.user.get_by_email(store, user.email) == user


def test_get_by_email_non_existing(store: Store):
    with pytest.raises(exceptions.NotFoundError):
        repo.user.get_by_email(store, "non@existing.com")


def _create_random_questions_answers(user):
    questions = factories.QuestionFactory.create_batch(random.randint(1, 4), user=user)
    factories.AnswerFactory.create_batch(
        random.randint(1, 4), question=questions[0], user=user
    )


def test_get_with_counts(store: Store, user, max_num_queries):
    _create_random_questions_answers(user)

    with max_num_queries(1):
        from_db = repo.user.get_with_counts(store, user.id)

        assert from_db == user
        assert from_db.question_count
        assert from_db.answer_count

    assert (
        from_db.question_count
        == store.db.query(Question).filter(Question.user_id == user.id).count()
    )
    assert (
        from_db.answer_count
        == store.db.query(Answer).filter(Answer.user_id == user.id).count()
    )


@pytest.mark.parametrize(
    ("page", "per_page", "n_pages", "exp_slice"),
    [
        (1, 4, 1, (0, 4)),
        (1, 2, 2, (0, 2)),
        (2, 2, 2, (2, 4)),
        (1, 3, 2, (0, 3)),
    ],
)
def test_list(store: Store, users, page, per_page, n_pages, exp_slice, max_num_queries):
    with max_num_queries(2):
        paginator = repo.user.list(store, page=page, per_page=per_page)

    assert paginator.objects == users[slice(*exp_slice)]
    assert paginator.total == len(users)
    assert paginator.page == page
    assert paginator.per_page == per_page
    assert len(paginator) == n_pages


def test_list_counts(store: Store, users):
    for user in users:
        _create_random_questions_answers(user)

    paginator = repo.user.list(store)

    for user in paginator.objects:
        assert (
            user.question_count
            == store.db.query(Question).filter(Question.user_id == user.id).count()
        )
        assert (
            user.answer_count
            == store.db.query(Answer).filter(Answer.user_id == user.id).count()
        )


@pytest.fixture
def data():
    return {
        "email": "info@test.com",
        "name": "Test User",
        "password": "123qweasd",
    }


def test_create(store: Store, data):
    user = repo.user.create(store, **data)

    from_db = repo.user.get(store, user.id)
    assert from_db == user
    assert from_db.email == data["email"]
    assert from_db.name == data["name"]
    assert check_password(data["password"], from_db.password)


def test_create_already_exists(store: Store, user, data):
    data["email"] = user.email

    with pytest.raises(exceptions.AlreadyExistsError):
        user = repo.user.create(store, **data)


def test_change_password(store: Store, user):
    repo.user.change_password(store, user, "new_password")

    assert check_password("new_password", user.password)

    from_db = repo.user.get(store, user.id)
    assert check_password("new_password", from_db.password)


def test_reset_password(store: Store, user):
    repo.user.reset_password(store, user)
    assert user.password is None

    from_db = repo.user.get(store, user.id)
    assert from_db.password is None


def test_update_info(store: Store, user):
    repo.user.update_info(store, user, name="New name")

    from_db = repo.user.get(store, user.id)
    assert user.name == from_db.name == "New name"


@pytest.mark.parametrize("user__email_verified", [False])
def test_mark_email_verified(store: Store, user):
    assert not user.email_verified

    repo.user.mark_email_verified(store, user)

    from_db = repo.user.get(store, user.id)
    assert user.email_verified is from_db.email_verified is True
