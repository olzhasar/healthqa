from crud.user import create_user, email_exists, get_by_email
from models.user import User


def test_get_by_email(db, user, other_user):
    assert get_by_email(db, user.email) == user
    assert get_by_email(db, other_user.email) == other_user != user
    assert get_by_email(db, "unexisting@person.com") is None


def test_email_exists(db, user):
    assert email_exists(db, user.email)
    assert not email_exists(db, "unexisting@person.com")


def test_create_user(db):
    user = create_user(
        db,
        email="vincent@vega.com",
        name="Vincent Vega",
        password="123qweasd",
    )

    assert isinstance(user, User)
    assert user.id
    assert db.query(User).filter(User.id == user.id).first() == user
