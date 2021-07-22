import crud
from app.security import check_password
from models.user import User


def test_get_by_email(db, user, other_user):
    assert crud.user.get_by_email(db, user.email) == user
    assert crud.user.get_by_email(db, other_user.email) == other_user != user
    assert crud.user.get_by_email(db, "unexisting@person.com") is None


def test_email_exists(db, user):
    assert crud.user.email_exists(db, user.email)
    assert not crud.user.email_exists(db, "unexisting@person.com")


def test_create_user(db):
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
