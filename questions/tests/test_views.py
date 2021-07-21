import pytest
from faker import Faker
from sqlalchemy import func

from models import Answer, Comment, Question
from tests.utils import full_url_for

fake = Faker()


class TestAskQuestion:
    url = "/questions/ask"

    @pytest.fixture
    def data(self):
        return {
            "title": "Test title corresponding to reuqirements",
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

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("title", "short"),
            ("title", fake.words(30)),
            ("content", "short"),
        ],
    )
    def test_fields_length_validation(self, as_user, data, db, field_name, field_value):
        data[field_name] = field_value

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert db.query(func.count(Question.id)).scalar() == 0

    def test_unauthorized(self, client, db):
        response = client.post(
            self.url,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert db.query(func.count(Question.id)).scalar() == 0


class TestAnswer:
    url = "/questions/{id}/answer"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, client, db, question, data):
        response = client.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert db.query(func.count(Answer.id)).scalar() == 0

    def test_ok(self, as_user, user, db, question, data):
        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 201

        answer = db.query(Answer).filter(Answer.question_id == question.id).first()

        assert answer
        assert answer.user == user
        assert answer.content == data["content"]

    def test_unexisting_question_id(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 403
        assert response.json == {"error": "invalid question_id"}

        assert db.query(func.count(Answer.id)).scalar() == 0


class TestAnswerComment:
    url = "/answers/{id}/comment"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, client, db, answer, data):
        response = client.post(
            self.url.format(id=answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert db.query(func.count(Comment.id)).scalar() == 0

    def test_ok(self, as_user, user, db, answer, data):
        response = as_user.post(
            self.url.format(id=answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 201

        comment = db.query(Comment).filter(Comment.answer_id == answer.id).first()

        assert comment
        assert comment.user == user
        assert comment.content == data["content"]
        assert comment.question is None

    def test_unexisting_answer_id(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid answer_id"}

        assert db.query(func.count(Comment.id)).scalar() == 0


class TestQuestionComment:
    url = "/questions/{id}/comment"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, client, db, question, data):
        response = client.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert db.query(func.count(Comment.id)).scalar() == 0

    def test_ok(self, as_user, user, db, question, data):
        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 201

        comment = db.query(Comment).filter(Comment.question_id == question.id).first()

        assert comment
        assert comment.user == user
        assert comment.content == data["content"]
        assert comment.answer is None

    def test_unexisting_question(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid question_id"}

        assert db.query(func.count(Comment.id)).scalar() == 0
