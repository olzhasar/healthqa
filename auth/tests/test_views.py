import secrets
from unittest.mock import MagicMock

import freezegun
import pytest
from pytest_mock.plugin import MockerFixture
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from auth import security
from models.user import User
from tests.utils import full_url_for


@pytest.fixture
def mock_generate_and_send_verification_link(mocker: MockerFixture):
    return mocker.patch("auth.views.generate_and_send_verification_link")


@pytest.fixture
def mock_generate_and_send_password_reset_link(mocker: MockerFixture):
    return mocker.patch("auth.views.generate_and_send_password_reset_link")


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

    def test_ok(
        self,
        client,
        db: Session,
        mock_generate_and_send_verification_link: MagicMock,
        data,
    ):
        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("auth.verification_required")

        user = db.query(User).filter(User.email == data["email"]).one()
        assert user.id
        assert security.check_password(data["password"], user.password)

        mock_generate_and_send_verification_link.assert_called_once_with(user)

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
        return security.hash_password("123qweasd")

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

    @pytest.mark.parametrize("user__email_verified", [False])
    def test_email_not_verified(
        self,
        client,
        db: Session,
        user,
        mock_generate_and_send_verification_link: MagicMock,
    ):
        response = client.post(
            self.url,
            data=dict(email=user.email, password="123qweasd"),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("auth.verification_required")

        mock_generate_and_send_verification_link.assert_called_once_with(user)

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


class TestVerificationRequired:
    url = "/verification_required"

    def test_ok(self, client):
        response = client.get(self.url)

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
        return security.hash_password("old_password")

    @pytest.fixture
    def data(self):
        return {
            "current_password": "old_password",
            "password": "123qweasd",
            "password_repeat": "123qweasd",
        }

    def test_get(self, db: Session, as_user):
        response = as_user.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_ok(self, db: Session, as_user, user, data):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("users.profile", id=user.id)

        db.refresh(user)
        assert security.check_password(data["password"], user.password)

    def test_wrong_old_password(self, db: Session, as_user, user, data):
        data["current_password"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert security.check_password("old_password", user.password)

    def test_passwords_mismatch(self, db: Session, as_user, user, data):
        data["password_repeat"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert security.check_password("old_password", user.password)

    def test_not_logged_in(self, client):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302


class TestForgotPassword:
    url = "/forgot_password"

    def test_get(self, client):
        response = client.get(self.url, follow_redirects=False)
        assert response.status_code == 200

    def test_post_ok(
        self, client, user, mock_generate_and_send_password_reset_link: MagicMock
    ):
        response = client.post(
            self.url,
            data={"email": user.email},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location == full_url_for("auth.forgot_password_sent")

        mock_generate_and_send_password_reset_link.assert_called_once_with(user)

    def test_post_unexisting(
        self, client, mock_generate_and_send_password_reset_link: MagicMock
    ):
        response = client.post(
            self.url,
            data={"email": "unexisting@example.com"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location == full_url_for("auth.forgot_password_sent")

        mock_generate_and_send_password_reset_link.assert_not_called()


class TestForgotPasswordSent:
    url = "/forgot_password_sent"

    def test_ok(self, client):
        response = client.get(self.url, follow_redirects=False)
        assert response.status_code == 200


class TestResetPassword:
    url = "/reset_password/{token}"

    def test_ok(self, db: Session, client, user):
        token = security.make_url_safe_token(user.id)

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("auth.set_password")

        db.refresh(user)
        assert user.password is None

    def test_invalid_token(self, db: Session, client, user):
        token = secrets.token_urlsafe()

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert user.password is not None

    def test_invalid_user(self, db: Session, client):
        token = security.make_url_safe_token(999)

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_expired_token(self, db: Session, client, user):
        with freezegun.freeze_time("2020-01-01 12:00:00") as frozen:
            token = security.make_url_safe_token(user.id)

            frozen.move_to("2021-01-01 12:00:00")

            response = client.get(
                self.url.format(token=token),
                follow_redirects=False,
            )

            assert response.status_code == 200

            db.refresh(user)
            assert user.password is not None


class TestSetPassword:
    url = "/set_password"

    @pytest.fixture
    def user__password(self):
        return None

    @pytest.fixture
    def data(self):
        return {
            "password": "123qweasd",
            "password_repeat": "123qweasd",
        }

    def test_get(self, as_user, user):
        response = as_user.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 200

    @pytest.mark.parametrize("user__password", ["not_empty"])
    def test_get_password_not_empty(self, as_user, user):
        response = as_user.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 403

    def test_get_unauthorized(self, client):
        response = client.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 403

    def test_post_ok(self, db: Session, as_user, user, data):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("users.profile", id=user.id)

        db.refresh(user)
        assert security.check_password("123qweasd", user.password)

    def test_post_error(self, db: Session, as_user, user, data):
        data["password_repeat"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert not user.password

    @pytest.mark.parametrize("user__password", ["not_empty"])
    def test_post_password_not_empty(self, db: Session, as_user, user, data):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 403

        db.refresh(user)
        assert not security.check_password("123qweasd", user.password)

    def test_post_unauthorized(self, client, data):
        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 403


class TestVerifyEmail:
    url = "/verify_email/{token}"

    @pytest.fixture()
    def user__email_verified(self):
        return False

    def test_ok(self, db: Session, client, user):
        token = security.make_url_safe_token(user.id)

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

        db.refresh(user)
        assert user.email_verified is True

    def test_invalid_token(self, db: Session, client, user):
        token = secrets.token_urlsafe()

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(user)
        assert user.email_verified is False

    def test_invalid_user(self, db: Session, client):
        token = security.make_url_safe_token(999)

        response = client.get(
            self.url.format(token=token),
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_expired_token(self, db: Session, client, user):
        with freezegun.freeze_time("2020-01-01 12:00:00") as frozen:
            token = security.make_url_safe_token(user.id)

            frozen.move_to("2021-01-01 12:00:00")

            response = client.get(
                self.url.format(token=token),
                follow_redirects=False,
            )

            assert response.status_code == 200

            db.refresh(user)
            assert user.email_verified is False
