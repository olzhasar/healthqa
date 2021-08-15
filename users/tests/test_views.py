import pytest
from sqlalchemy.orm.session import Session

from tests.utils import full_url_for


def test_all(db: Session, client):
    url = "/users/"

    response = client.get(url)
    assert response.status_code == 200


class TestProfile:
    url = "/users/{id}/"

    def test_ok(self, db: Session, client, user):
        response = client.get(self.url.format(id=user.id))

        assert response.status_code == 200

    def test_non_existing(self, db: Session, client, user):
        response = client.get(self.url.format(id=999))

        assert response.status_code == 404


class TestEditProfile:
    url = "/users/{id}/edit"

    @pytest.fixture
    def data(self):
        return {"name": "New name"}

    def test_get_ok(self, as_user, user):
        response = as_user.get(self.url.format(id=user.id))

        assert response.status_code == 200

    def test_get_wrong_user(self, as_user, other_user):
        response = as_user.get(self.url.format(id=other_user.id))

        assert response.status_code == 404

    def test_get_unauthorized(self, client, user):
        response = client.get(self.url.format(id=user.id), follow_redirects=False)

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_ok(self, db: Session, as_user, user, data):
        response = as_user.post(
            self.url.format(id=user.id),
            follow_redirects=False,
            data=data,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("users.profile", id=user.id)

    def test_post_missing_data(self, db: Session, as_user, user):
        response = as_user.post(
            self.url.format(id=user.id),
            follow_redirects=False,
            data={},
        )

        assert response.status_code == 200
