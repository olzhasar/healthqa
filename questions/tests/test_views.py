import pytest
from faker import Faker
from pytest_factoryboy import LazyFixture
from sqlalchemy import func

from models import Answer, Comment, Question, Vote
from tests import factories
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


class TestDetails:
    url = "/questions/{id}"

    @pytest.fixture
    def question(self):
        obj = factories.QuestionFactory()

        factories.CommentFactory.create_batch(2, entry_id=obj.id)
        factories.VoteFactory.create_batch(2, entry_id=obj.id)

        for answer in factories.AnswerFactory.create_batch(2, question=obj):
            factories.CommentFactory.create_batch(2, entry_id=answer.id)
            factories.VoteFactory.create_batch(2, entry_id=answer.id)

        return obj

    def test_ok(self, client, db, question, max_num_queries):
        with max_num_queries(1):
            response = client.get(self.url.format(id=question.id))

        assert response.status_code == 200

    def test_unexisting_question(self, client):
        response = client.get(self.url.format(id=999))

        assert response.status_code == 404


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
        assert response.status_code == 200

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
    url = "/entries/{id}/comment"

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
        assert response.status_code == 200

        comment = db.query(Comment).filter(Comment.entry_id == answer.id).first()

        assert comment
        assert comment.user == user
        assert comment.content == data["content"]

    def test_unexisting_answer_id(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid entry_id"}

        assert db.query(func.count(Comment.id)).scalar() == 0


class TestQuestionComment:
    url = "/entries/{id}/comment"

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
        assert response.status_code == 200

        comment = db.query(Comment).filter(Comment.entry_id == question.id).first()

        assert comment
        assert comment.user == user
        assert comment.content == data["content"]

    def test_unexisting_question(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid entry_id"}

        assert db.query(func.count(Comment.id)).scalar() == 0


class TestVote:
    url = "/entries/{id}/vote"

    @pytest.fixture(
        params=[
            LazyFixture("question"),
            LazyFixture("answer"),
            LazyFixture("question_comment"),
            LazyFixture("answer_comment"),
        ]
    )
    def instance(self, request):
        return request.param.evaluate(request)

    @pytest.mark.parametrize("value", [-1, 1])
    def test_new_vote(self, db, as_user, user, value, instance):
        response = as_user.post(
            self.url.format(id=instance.id),
            data={"value": value},
        )

        assert response.status_code == 200

        from_db = db.query(Vote).filter(Vote.entry_id == instance.id).first()

        assert from_db
        assert from_db.id
        assert from_db.entry == instance

    def test_delete_ok(self, db, as_user, user, instance):
        factories.VoteFactory(entry_id=instance.id)

        response = as_user.post(
            self.url.format(id=instance.id),
            data={"value": 0},
        )

        assert response.status_code == 200

        assert not bool(
            db.query(Vote.id)
            .filter(Vote.entry_id == instance.id, Vote.user_id == user.id)
            .first()
        )
