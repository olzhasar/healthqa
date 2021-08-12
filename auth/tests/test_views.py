import pytest
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from app.security import check_password
from models.user import User
from tests.utils import full_url_for


class TestSignup:
    url = "/signup"

    @pytest.fixture
    def data(self):
        return {
            "name": "Vincent Vega",
            "email": "vincent@vega.com",
            "password": "123qweasd",
            "password_repeat": "123qweasd",
        }

    def test_get(self, client):
        response = client.get(self.url)

        assert response.status_code == 200

    def test_get_already_authenticated(self, as_user):
        response = as_user.get(self.url, follow_redirects=False)

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

    def test_ok(self, client, data, db):
        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

        created = db.query(User).filter(User.email == data["email"]).first()
        assert created
        assert created.id
        assert check_password(data["password"], created.password)

    def test_email_exists(self, client, data, db, user):
        data["email"] = user.email

        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(User.id)).scalar() == 1

    @pytest.mark.parametrize(
        "missing_field",
        [
            "email",
            "name",
            "password",
            "password_repeat",
        ],
    )
    def test_field_missing(self, client, data, db, missing_field):
        data.pop(missing_field)

        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(User.id)).scalar() == 0

    def test_passwords_mismatch(self, client, data, db):
        data["password_repeat"] = "wrong_password"

        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(User.id)).scalar() == 0

    def test_wrong_email(self, client, data, db):
        data["email"] = "aslkfja@aslfas"

        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(User.id)).scalar() == 0

    def test_password_min_length(self, client, data, db):
        data["password"] = "123"
        data["password_repeat"] = "123"

        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(User.id)).scalar() == 0


class TestLogin:
    url = "/login"

    @pytest.fixture
    def user__password(self):
        return "123qweasd"

    def test_get(self, client):
        response = client.get(self.url)

        assert response.status_code == 200

    def test_get_already_authenticated(self, as_user, user):
        response = as_user.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

    def test_ok(self, client, db, user):
        response = client.post(
            self.url,
            data=dict(email=user.email, password="123qweasd"),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

    def test_wrong_password(self, client, db, user):
        response = client.post(
            self.url,
            data=dict(email=user.email, password="wrong_password"),
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_user_not_found(self, client, db):
        response = client.post(
            self.url,
            data=dict(email="wrong@email.com", password="123qweasd"),
            follow_redirects=False,
        )

        assert response.status_code == 200


class TestLogout:
    url = "/logout"

    def test_ok(self, as_user):
        response = as_user.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

    def test_not_logged_in(self, client):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 401


class TestChangePassword:
    url = "/change_password"

    @pytest.fixture
    def user__password(self):
        return "old_password"

    @pytest.fixture
    def data(self):
        return {
            "current_password": "old_password",
            "password": "123qweasd",
            "password_repeat": "123qweasd",
        }

    def test_ok(self, db: Session, as_user, user, data):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("users.profile", id=user.id)

        db.refresh(user)
        assert check_password(data["password"], user.password)

    def test_wrong_old_password(self, db: Session, as_user, user, data):
        data["current_password"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert check_password("old_password", user.password)

    def test_passwords_mismatch(self, db: Session, as_user, user, data):
        data["password_repeat"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert check_password("old_password", user.password)

    def test_not_logged_in(self, client):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
