import random

import pytest
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import func

import crud
from app.security import check_password
from models import Entry, User
from tests import factories


def test_get_by_email(db: Session, user, other_user):
    assert crud.user.get_by_email(db, email=user.email) == user
    assert crud.user.get_by_email(db, email=other_user.email) == other_user != user
    assert crud.user.get_by_email(db, email="unexisting@person.com") is None


def test_email_exists(db: Session, user):
    assert crud.user.email_exists(db, email=user.email)
    assert not crud.user.email_exists(db, email="unexisting@person.com")


def test_create_user(db: Session):
    user = crud.user.create_user(
        db,
        email="vincent@vega.com",
        name="Vincent Vega",
        password="123qweasd",
    )

    assert isinstance(user, User)
    assert user.id
    assert user.email == "vincent@vega.com"
    assert user.name == "Vincent Vega"
    assert check_password("123qweasd", user.password)
    assert db.query(User).filter(User.id == user.id).first() == user


def _create_questions_answers(user: User):
    questions = factories.QuestionFactory.create_batch(random.randint(1, 4), user=user)
    factories.AnswerFactory.create_batch(
        random.randint(1, 4), question=questions[0], user=user
    )


@pytest.fixture
def users():
    users = factories.UserFactory.create_batch(5)

    for user in users:
        _create_questions_answers(user)

    return users


@pytest.fixture
def user_questions_answers(user):
    _create_questions_answers(user)


def assert_user_counts_match_db(db: Session, user: User):
    assert (
        user.question_count
        == db.query(func.count(Entry.id))
        .where(Entry.user_id == user.id, Entry.type == 1)
        .scalar()
    )
    assert (
        user.answer_count
        == db.query(func.count(Entry.id))
        .where(Entry.user_id == user.id, Entry.type == 2)
        .scalar()
    )


def test_for_list(db: Session, users, max_num_queries):
    with max_num_queries(1):
        result = crud.user.for_list(db)
        for user in result:
            assert user.question_count
            assert user.answer_count

    assert set(result) == set(users)

    for user in result:
        assert_user_counts_match_db(db, user)


def test_get_with_counts(db: Session, user, user_questions_answers, max_num_queries):
    with max_num_queries(1):
        result = crud.user.get_with_counts(db, id=user.id)
        assert isinstance(result, User)
        assert result.question_count
        assert result.answer_count

    assert_user_counts_match_db(db, result)
