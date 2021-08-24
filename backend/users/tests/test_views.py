from sqlalchemy.orm.session import Session


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