from flask.app import Flask

from auth.security import check_password
from models.user import User


def test_create_user(db, app: Flask):
    runner = app.test_cli_runner()

    data = ["info@test.com", "Test", "123qweasd"]

    runner.invoke(args=["create_user"], input="\n".join(data))

    from_db: User = db.query(User).filter(User.email == "info@test.com").one()

    assert from_db.name == "Test"
    assert from_db.email_verified
    assert check_password("123qweasd", from_db.password)
