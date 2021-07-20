import pytest
from faker import Faker
from sqlalchemy import func

from models import Question
from tests.utils import full_url_for

fake = Faker()


class TestAskQuestion:
    url = "/questions/ask"

    @pytest.fixture
    def data(self):
        return {
            "title": "Test title",
            "content": fake.paragraph(),
        }

    def test_ok(self, as_user, user, data, db):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location == full_url_for("home.index")

        question = db.query(Question).filter(Question.user_id == user.id).first()

        assert question
        assert question.title == data["title"]
        assert question.content == data["content"]

    @pytest.mark.parametrize("missing_field", ["title", "content"])
    def test_missing_fields(self, as_user, user, data, missing_field, db):
        data.pop(missing_field)

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(Question.id)).scalar() == 0

    def test_content_short(self, as_user, data, db):
        data["content"] = "short"

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(Question.id)).scalar() == 0

    def test_not_logged_in(self, client, db):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("home.index"))

        assert db.query(func.count(Question.id)).scalar() == 0
