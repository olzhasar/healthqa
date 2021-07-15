from crud.users import create_user, get_by_email, get_by_username
from models.user import User


def test_get_by_email(db, user, other_user):
    assert get_by_email(db, user.email) == user
    assert get_by_email(db, other_user.email) == other_user != user
    assert get_by_email(db, "unexisting@person.com") is None


def test_get_by_username(db, user, other_user):
    assert get_by_username(db, user.username) == user
    assert get_by_username(db, other_user.username) == other_user != user
    assert get_by_username(db, "unexisting") is None


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
