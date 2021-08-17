from datetime import datetime

import pytest
from faker import Faker
from pytest_factoryboy import LazyFixture
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from models import Answer, Comment, Question, Vote
from tests import factories
from tests.utils import full_url, full_url_for

fake = Faker()


class TestAskQuestion:
    url = "/questions/ask"

    @pytest.fixture
    def tags(self):
        return factories.TagFactory.create_batch(3)

    @pytest.fixture
    def data(self, tags):
        return {
            "title": "Test title corresponding to requirements",
            "content": fake.paragraph(),
            "tags": [t.id for t in tags],
        }

    def test_ok(self, as_user, user, data, db, tags):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        question = db.query(Question).filter(Question.user_id == user.id).first()

        assert response.status_code == 302
        assert response.location == full_url(question.url)

        assert question
        assert question.title == data["title"]
        assert question.content == data["content"]
        assert question.tags == tags

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


class TestAllQuestions:
    url = "/questions/"

    def test_ok(self, client, max_num_queries):
        with max_num_queries(3):
            response = client.get(self.url)

        assert response.status_code == 200


class TestDetails:
    url = "/questions/{id}"

    def test_ok(self, client, db, question_with_related, max_num_queries):
        with max_num_queries(3):
            response = client.get(self.url.format(id=question_with_related.id))

        assert response.status_code == 200

    def test_unexisting_question(self, client):
        response = client.get(self.url.format(id=999))

        assert response.status_code == 404


class TestEditQuestion:
    url = "/questions/{id}/edit"

    @pytest.fixture
    def tags(self):
        return factories.TagFactory.create_batch(3)

    @pytest.fixture
    def data(self, tags):
        return {
            "title": fake.sentence(),
            "content": fake.paragraph(),
            "tags": [],
        }

    def test_get(self, db: Session, as_user, question):
        response = as_user.get(
            self.url.format(id=question.id),
            follow_redirects=False,
        )
        assert response.status_code == 200

    def test_not_found(self, db: Session, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_get_unauthorized(self, db: Session, client, question):
        response = client.get(
            self.url.format(id=question.id),
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    @pytest.mark.parametrize("question__user", [LazyFixture("other_user")])
    def test_get_wrong_user(self, as_user, other_user, question):
        response = as_user.get(
            self.url.format(id=question.id),
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_post_ok(self, db: Session, as_user, question, data):
        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location == full_url(question.url)

        db.refresh(question)
        assert question.title == data["title"]
        assert question.content == data["content"]

    def test_post_unauthorized(self, db: Session, client, question, data):
        response = client.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_error(self, db: Session, as_user, question, data):
        data["content"] = "short"

        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 200

        db.refresh(question)
        assert question.title != data["title"]
        assert question.content != data["content"]


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


class TestEditAnswer:
    url = "/answers/{id}/edit"

    @pytest.fixture
    def new_content(self):
        return fake.paragraph()

    def test_get(self, db: Session, as_user, answer):
        response = as_user.get(
            self.url.format(id=answer.id),
            follow_redirects=False,
        )
        assert response.status_code == 200

    def test_not_found(self, db: Session, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_get_unauthorized(self, db: Session, client, answer):
        response = client.get(
            self.url.format(id=answer.id),
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    @pytest.mark.parametrize("answer__user", [LazyFixture("other_user")])
    def test_get_wrong_user(self, as_user, other_user, answer):
        response = as_user.get(
            self.url.format(id=answer.id),
            follow_redirects=False,
        )
        assert response.status_code == 403

    def test_post_ok(self, db: Session, as_user, answer, new_content):
        response = as_user.post(
            self.url.format(id=answer.id),
            data={"content": new_content},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location == full_url(answer.url)

        db.refresh(answer)
        assert answer.content == new_content

    def test_post_unauthorized(self, db: Session, client, answer, new_content):
        response = client.post(
            self.url.format(id=answer.id),
            data={"content": new_content},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_error(self, db: Session, as_user, answer, new_content):
        response = as_user.post(
            self.url.format(id=answer.id),
            data={"content": "short"},
            follow_redirects=False,
        )
        assert response.status_code == 200

        db.refresh(answer)
        assert answer.content != new_content


class TestComment:
    url = "/entries/{id}/comment"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, client, db, question_or_answer, data):
        response = client.post(
            self.url.format(id=question_or_answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert db.query(func.count(Comment.id)).scalar() == 0

    def test_ok(self, as_user, user, db, question_or_answer, data):
        response = as_user.post(
            self.url.format(id=question_or_answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 200

        comment = (
            db.query(Comment).filter(Comment.entry_id == question_or_answer.id).first()
        )

        assert comment
        assert comment.user == user
        assert comment.content == data["content"]

    def test_unexisting_entry(self, as_user, db, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid entry_id"}

        assert db.query(func.count(Comment.id)).scalar() == 0


class TestEditComment:
    url = "/comments/{id}/edit"

    @pytest.fixture(
        params=[
            LazyFixture("question_comment"),
            LazyFixture("answer_comment"),
        ]
    )
    def comment(self, request):
        return request.param.evaluate(request)

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_get(self, db: Session, as_user, comment):
        response = as_user.get(
            self.url.format(id=comment.id),
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_get_unexisting(self, db: Session, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )

        assert response.status_code == 404

    def test_get_unauthorized(self, db: Session, client, comment):
        response = client.get(
            self.url.format(id=comment.id),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_ok(self, db: Session, as_user, comment, data):
        response = as_user.post(
            self.url.format(id=comment.id),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(comment)
        assert comment.content == data["content"]

    def test_post_invalid_data(self, db: Session, as_user, comment):
        response = as_user.post(
            self.url.format(id=comment.id),
            data={"content": "short"},
            follow_redirects=False,
        )

        assert response.status_code == 200

        db.refresh(comment)
        assert comment.content != "short"

    def test_post_unexisting(self, db: Session, as_user, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 404

    def test_post_unauthorized(self, db: Session, client, comment, data):
        response = client.post(
            self.url.format(id=comment.id),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))


class TestVote:
    url = "/entries/{id}/vote/{value}"

    def test_new_vote(self, db: Session, as_user, user, question):
        response = as_user.post(
            self.url.format(id=question.id, value=1),
        )

        assert response.status_code == 200

        from_db = db.query(Vote).filter(Vote.entry_id == question.id).first()

        assert from_db
        assert from_db.entry == question
        assert from_db.value == 1

    def test_update_existing(self, db: Session, as_user, user, question):
        existing = factories.VoteFactory(user=user, entry_id=question.id, value=-1)

        response = as_user.post(
            self.url.format(id=question.id, value=1),
        )

        assert response.status_code == 200

        db.refresh(existing)
        assert existing.value == 1

    def test_delete(self, db: Session, as_user, user, question):
        factories.VoteFactory(user=user, entry_id=question.id, value=1)

        response = as_user.post(
            self.url.format(id=question.id, value=0),
        )

        assert response.status_code == 200

        assert not bool(
            db.query(Vote.id)
            .filter(Vote.user_id == user.id, Vote.entry_id == question.id)
            .first()
        )

    def test_error(self, db: Session, as_user, user, question):
        response = as_user.post(
            self.url.format(id=question.id, value=5),
        )

        assert response.status_code == 400
        assert response.json == {"error": "Invalid vote value"}

        assert not bool(
            db.query(Vote.id)
            .filter(Vote.user_id == user.id, Vote.entry_id == question.id)
            .first()
        )


class TestDeleteEntry:
    url = "/entries/{id}"

    @pytest.mark.freeze_time("2030-01-01")
    def test_ok(self, db: Session, as_user, entry):
        response = as_user.delete(self.url.format(id=entry.id))

        assert response.status_code == 204

        db.refresh(entry)
        assert entry.deleted_at == datetime(2030, 1, 1)

    def test_unexisting_question(self, as_user):
        response = as_user.delete(self.url.format(id=999))

        assert response.status_code == 404

    def test_unauthorized(self, client, entry):
        response = client.delete(self.url.format(id=entry.id), follow_redirects=False)

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))
