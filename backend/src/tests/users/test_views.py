import pytest
from sqlalchemy.orm.session import Session

from tests.factories import UserFactory


@pytest.mark.allow_db
def test_all(client, template_rendered):
    UserFactory.create_batch(3)

    url = "/users/"

    response = client.get(url)
    assert response.status_code == 200
    assert template_rendered("users/list.html")


@pytest.mark.allow_db
@pytest.mark.allow_redis
class TestProfile:
    url = "/users/{id}/"

    def test_ok(self, db: Session, client, user, template_rendered):
        response = client.get(self.url.format(id=user.id))

        assert response.status_code == 200
        assert template_rendered("users/profile.html")

    def test_question_tab(self, db: Session, client, question, template_rendered):
        response = client.get(self.url.format(id=question.user.id) + "?tab=questions")

        assert response.status_code == 200
        assert template_rendered("users/profile.html")

    def test_answer_tab(self, db: Session, client, answer, template_rendered):
        response = client.get(self.url.format(id=answer.user.id))

        assert response.status_code == 200
        assert template_rendered("users/profile.html")

    def test_non_existing(self, db: Session, client):
        response = client.get(self.url.format(id=999))

        assert response.status_code == 404
