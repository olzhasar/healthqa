from crud.users import (
    create_user,
    email_exists,
    get_by_email,
    get_by_username,
    username_exists,
    username_or_email_taken,
)
from models.user import User


def test_get_by_email(db, user, other_user):
    assert get_by_email(db, user.email) == user
    assert get_by_email(db, other_user.email) == other_user != user
    assert get_by_email(db, "unexisting@person.com") is None


def test_email_exists(db, user):
    assert email_exists(db, user.email)
    assert not email_exists(db, "unexisting@person.com")


def test_get_by_username(db, user, other_user):
    assert get_by_username(db, user.username) == user
    assert get_by_username(db, other_user.username) == other_user != user
    assert get_by_username(db, "unexisting") is None


def test_username_exists(db, user):
    assert username_exists(db, user.username)
    assert not username_exists(db, "unexisting_username")


def test_create_user(db, user):
    user = create_user(
        db,
        username="test_user",
        email="vincent@vega.com",
        password="123qweasd",
    )

    assert isinstance(user, User)
    assert user.id
    assert db.query(User).filter(User.id == user.id).first() == user


def test_username_or_email_taken(db, user):
    assert username_or_email_taken(db, user.username, user.email)
    assert username_or_email_taken(db, user.username, "other_email")
    assert username_or_email_taken(db, "other_username", user.email)
    assert not username_or_email_taken(db, "other_username", "other_email")
