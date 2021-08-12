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


@pytest.fixture
def users():
    users = factories.UserFactory.create_batch(5)

    for user in users:
        questions = factories.QuestionFactory.create_batch(
            random.randint(1, 4), user=user
        )
        factories.AnswerFactory.create_batch(
            random.randint(1, 4), question=questions[0], user=user
        )
        factories.CommentFactory.create_batch(
            random.randint(1, 4), entry_id=questions[0].id, user=user
        )

    return users


def test_for_list(db: Session, users, max_num_queries):
    with max_num_queries(1):
        result = crud.user.for_list(db)

    assert set(result) == set(users)

    for user in result:
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
        assert (
            user.comment_count
            == db.query(func.count(Entry.id))
            .where(Entry.user_id == user.id, Entry.type == 3)
            .scalar()
        )
