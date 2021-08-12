import pytest
from faker import Faker
from pytest_factoryboy import LazyFixture
from sqlalchemy import func

from models import Answer, Comment, Entry, Question, Vote
from tests import factories
from tests.utils import full_url_for

fake = Faker()


class TestAskQuestion:
    url = "/questions/ask"

    @pytest.fixture
    def data(self):
        return {
            "title": "Test title corresponding to requirements",
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
        assert not bool(
            db.query(Question.id).filter(Question.user_id == user.id).first()
        )

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("title", "short"),
            ("title", fake.pystr(min_chars=151, max_chars=160)),
            ("content", "short"),
        ],
    )
    def test_fields_length_validation(
        self, as_user, user, data, db, field_name, field_value
    ):
        data[field_name] = field_value

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert not bool(
            db.query(Question.id).filter(Question.title == data["title"]).first()
        )

    def test_unauthorized(self, client, data, db):
        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert not bool(
            db.query(Question.id).filter(Question.title == data["title"]).first()
        )


class TestDetails:
    url = "/questions/{id}"

    def test_ok(self, client, db, question_full, max_num_queries):
        with max_num_queries(1):
            response = client.get(self.url.format(id=question_full.id))

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
    url = "/entries/{id}/vote/{value}"

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

    @pytest.mark.parametrize(
        ("url_param", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_new_vote(self, db, as_user, user, instance, url_param, value):
        response = as_user.post(
            self.url.format(id=instance.id, value=url_param),
        )

        assert response.status_code == 200

        from_db = db.query(Vote).filter(Vote.entry_id == instance.id).first()

        assert from_db
        assert from_db.id
        assert from_db.entry == instance
        assert from_db.value == value

        assert db.query(Entry.score).filter(Entry.id == instance.id).scalar() == value

    @pytest.mark.parametrize(
        ("url_param", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_already_exists_same_value(
        self, db, as_user, user, instance, url_param, value
    ):
        factories.VoteFactory(user=user, entry_id=instance.id, value=value)

        response = as_user.post(
            self.url.format(id=instance.id, value=url_param),
        )

        assert response.status_code == 400
        assert response.json == {"error": "Vote already exists"}

    @pytest.mark.parametrize(
        ("url_param", "value"),
        [
            (1, 1),
            (2, -1),
        ],
    )
    def test_already_exists_different_value(
        self, db, as_user, user, instance, url_param, value
    ):
        existing = factories.VoteFactory(user=user, entry_id=instance.id, value=-value)

        response = as_user.post(
            self.url.format(id=instance.id, value=url_param),
        )

        assert response.status_code == 200

        db.refresh(existing)
        assert existing.value == value

    def test_invalid_vote_value(self, db, as_user, user, instance):
        response = as_user.post(
            self.url.format(id=instance.id, value=5),
        )

        assert response.status_code == 400
        assert response.json == {"error": "Invalid vote value"}

        assert not bool(db.query(Vote.id).filter(Vote.entry_id == instance.id).first())

    def test_delete_ok(self, db, as_user, user, instance):
        vote = factories.VoteFactory(user=user, entry_id=instance.id)

        assert (
            db.query(Entry.score).filter(Entry.id == instance.id).scalar() == vote.value
        )

        response = as_user.post(
            self.url.format(id=instance.id, value=0),
        )

        assert response.status_code == 200

        assert not bool(db.query(Vote.id).filter(Vote.entry_id == instance.id).first())

        assert db.query(Entry.score).filter(Entry.id == instance.id).scalar() == 0

    def test_delete_does_not_exist(self, db, as_user, user, instance):
        response = as_user.post(
            self.url.format(id=instance.id, value=0),
        )

        assert response.status_code == 400
        assert response.json == {"error": "Vote does not exist"}
