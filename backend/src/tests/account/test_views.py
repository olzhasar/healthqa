import pytest

from auth import security
from storage import Store
from tests.utils import full_url_for

pytestmark = [pytest.mark.allow_db]


class TestMain:
    url = "/account/info"

    @pytest.fixture
    def data(self):
        return {"name": "New name"}

    def test_get_ok(self, as_user, user):
        response = as_user.get(self.url)

        assert response.status_code == 200

    def test_get_unauthorized(self, client, user):
        response = client.get(self.url, follow_redirects=False)

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_ok(self, store: Store, as_user, user, data):
        response = as_user.post(
            self.url,
            follow_redirects=False,
            data=data,
        )

        assert response.status_code == 200

        store.refresh(user)
        assert user.name == data["name"]

    def test_post_missing_data(self, as_user, user):
        response = as_user.post(
            self.url,
            follow_redirects=False,
            data={},
        )

        assert response.status_code == 200


class TestChangePassword:
    url = "/account/change_password"

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

    def test_get(self, as_user):
        response = as_user.get(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_ok(self, store: Store, as_user, user, data):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("users.profile", id=user.id)

        store.refresh(user)
        assert security.check_password(data["password"], user.password)

    def test_wrong_old_password(self, store: Store, as_user, user, data):
        data["current_password"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        store.refresh(user)
        assert security.check_password("old_password", user.password)

    def test_passwords_mismatch(self, store: Store, as_user, user, data):
        data["password_repeat"] = "wrong_password"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        store.refresh(user)
        assert security.check_password("old_password", user.password)

    def test_not_logged_in(self, client):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
