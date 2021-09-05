from datetime import datetime

import pytest
from faker import Faker
from pytest_factoryboy import LazyFixture
from sqlalchemy.orm.session import Session

import repository as repo
from storage import Store
from tests import factories
from tests.utils import full_url_for

fake = Faker()

pytestmark = [pytest.mark.allow_db]


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

    def test_ok(self, store: Store, as_user, user, data, tags):
        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        question = repo.question.first_for_user(store, user)

        assert response.status_code == 302
        assert response.location == full_url_for(
            "questions.details", id=question.id, slug=question.slug
        )

        assert question
        assert question.title == data["title"]
        assert question.content == data["content"]
        assert question.tags == tags

    @pytest.mark.parametrize("missing_field", ["title", "content", "tags"])
    def test_missing_fields(self, store: Store, as_user, user, data, missing_field):
        data.pop(missing_field)

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert not repo.question.exists(store)

    @pytest.mark.parametrize(
        ("field_name", "field_value"),
        [
            ("title", "short"),
            ("title", fake.pystr(min_chars=151, max_chars=160)),
            ("content", "short"),
        ],
    )
    def test_fields_length_validation(
        self, store: Store, as_user, user, data, field_name, field_value
    ):
        data[field_name] = field_value

        response = as_user.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert not repo.question.exists(store)

    def test_unauthorized(self, store: Store, client, data):
        response = client.post(
            self.url,
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert not repo.question.exists(store)


@pytest.mark.allow_redis
class TestAllQuestions:
    url = "/questions/"

    def test_ok(self, client, max_num_queries):
        with max_num_queries(3):
            response = client.get(self.url)

        assert response.status_code == 200


class TestTags:
    url = "/tags/"

    def test_ok(self, client, max_num_queries):
        with max_num_queries(1):
            response = client.get(self.url)

        assert response.status_code == 200


@pytest.mark.allow_redis
class TestByTag:
    url = "/tags/{slug}/"

    def test_ok(self, client, tag, max_num_queries):
        with max_num_queries(4):
            response = client.get(self.url.format(slug=tag.slug))

        assert response.status_code == 200

    def test_unexisting_tag(self, client):
        response = client.get(self.url.format(slug="unexisting"))

        assert response.status_code == 404


@pytest.mark.allow_redis
class TestSearch:
    url = "/questions/search?q={query}"

    def test_ok(self, client, question, max_num_queries, template_rendered):
        with max_num_queries(3):
            response = client.get(self.url.format(query="something"))

        assert response.status_code == 200
        assert template_rendered("questions/search_results.html")


@pytest.mark.allow_redis
class TestDetails:
    url = "/questions/{id}/{slug}"

    def test_ok(self, client, question_with_related, max_num_queries):
        with max_num_queries(4):
            response = client.get(
                self.url.format(
                    id=question_with_related.id, slug=question_with_related.slug
                )
            )

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "url",
        [
            "/questions/{id}",
            "/questions/{id}/",
            "/questions/{id}/wrong-slug",
        ],
    )
    def test_redirect(self, client, question_with_related, url):
        response = client.get(url.format(id=question_with_related.id))

        assert response.status_code == 301
        assert response.location == full_url_for(
            "questions.details",
            id=question_with_related.id,
            slug=question_with_related.slug,
        )

    @pytest.mark.parametrize(
        "url",
        [
            "/questions/{id}",
            "/questions/{id}/",
            "/questions/{id}/wrong-slug",
        ],
    )
    def test_unexisting_question(self, client, url):
        response = client.get(url.format(id=999))

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
            "tags": [t.id for t in tags],
        }

    def test_get(self, as_user, question):
        response = as_user.get(
            self.url.format(id=question.id),
            follow_redirects=False,
        )
        assert response.status_code == 200

    def test_not_found(self, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_get_unauthorized(self, client, question):
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

    def test_post_ok(self, store: Store, as_user, question, data, tags):
        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location == full_url_for(
            "questions.details", id=question.id, slug=question.slug
        )

        store.refresh(question)
        assert question.title == data["title"]
        assert question.content == data["content"]
        assert question.tags == tags

    def test_post_unauthorized(self, store: Store, client, question, data):
        response = client.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        store.refresh(question)
        assert question.title != data["title"]
        assert question.content != data["content"]

    def test_post_error(self, store: Store, as_user, question, data):
        data["content"] = "short"

        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 200

        store.refresh(question)
        assert question.title != data["title"]
        assert question.content != data["content"]


class TestAnswer:
    url = "/questions/{id}/answer"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, store: Store, client, question, data):
        response = client.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert not repo.answer.exists(store)

    def test_ok(self, store: Store, as_user, user, question, data):
        response = as_user.post(
            self.url.format(id=question.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 200

        answer = repo.answer.first(store)

        assert answer
        assert answer.user == user
        assert answer.content == data["content"]

    def test_unexisting_question_id(self, store: Store, as_user, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 403
        assert response.json == {"error": "invalid question_id"}

        assert not repo.answer.exists(store)


class TestEditAnswer:
    url = "/answers/{id}/edit"

    @pytest.fixture
    def new_content(self):
        return fake.paragraph()

    def test_get(self, as_user, answer):
        response = as_user.get(
            self.url.format(id=answer.id),
            follow_redirects=False,
        )
        assert response.status_code == 200

    def test_not_found(self, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )
        assert response.status_code == 404

    def test_get_unauthorized(self, client, answer):
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

    def test_post_ok(self, store: Store, as_user, answer, new_content):
        response = as_user.post(
            self.url.format(id=answer.id),
            data={"content": new_content},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert (
            response.location
            == full_url_for("questions.details", id=answer.question.id)
            + f"#answer_{answer.id}"
        )

        store.refresh(answer)
        assert answer.content == new_content

    def test_post_unauthorized(self, store: Session, client, answer, new_content):
        response = client.post(
            self.url.format(id=answer.id),
            data={"content": new_content},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        store.refresh(answer)
        assert answer.content != new_content

    def test_post_error(self, store: Store, as_user, answer, new_content):
        response = as_user.post(
            self.url.format(id=answer.id),
            data={"content": "short"},
            follow_redirects=False,
        )
        assert response.status_code == 200

        store.refresh(answer)
        assert answer.content != new_content


class TestComment:
    url = "/entries/{id}/comment"

    @pytest.fixture
    def data(self):
        return {"content": fake.paragraph()}

    def test_unauthorized(self, store: Store, client, question_or_answer, data):
        response = client.post(
            self.url.format(id=question_or_answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        assert not repo.comment.exists(store)

    def test_ok(self, store: Store, as_user, user, question_or_answer, data):
        response = as_user.post(
            self.url.format(id=question_or_answer.id),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 200

        comment = repo.comment.first(store)

        assert comment.entry_id == question_or_answer.id
        assert comment.user == user
        assert comment.content == data["content"]

    def test_unexisting_entry(self, store: Store, as_user, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )
        assert response.status_code == 400
        assert response.json == {"error": "invalid entry_id"}

        assert not repo.comment.exists(store)


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

    def test_get(self, as_user, comment):
        response = as_user.get(
            self.url.format(id=comment.id),
            follow_redirects=False,
        )

        assert response.status_code == 200

    def test_get_unexisting(self, as_user):
        response = as_user.get(
            self.url.format(id=999),
            follow_redirects=False,
        )

        assert response.status_code == 404

    def test_get_unauthorized(self, client, comment):
        response = client.get(
            self.url.format(id=comment.id),
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

    def test_post_ok(self, store: Store, as_user, comment, data):
        response = as_user.post(
            self.url.format(id=comment.id),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 200

        store.refresh(comment)
        assert comment.content == data["content"]

    def test_post_invalid_data(self, store: Store, as_user, comment):
        response = as_user.post(
            self.url.format(id=comment.id),
            data={"content": "short"},
            follow_redirects=False,
        )

        assert response.status_code == 200

        store.refresh(comment)
        assert comment.content != "short"

    def test_post_unexisting(self, store: Store, as_user, data):
        response = as_user.post(
            self.url.format(id=999),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 404

    def test_post_unauthorized(self, store: Store, client, comment, data):
        response = client.post(
            self.url.format(id=comment.id),
            data=data,
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))

        store.refresh(comment)
        assert comment.content != data["content"]


class TestVote:
    url = "/entries/{id}/vote/{value}"

    def test_new_vote(self, store: Store, as_user, user, question):
        response = as_user.post(
            self.url.format(id=question.id, value=1),
        )

        assert response.status_code == 200

        vote = repo.vote.first(store)

        assert vote.user == user
        assert vote.entry == question
        assert vote.value == 1

    def test_update_existing(self, store: Store, as_user, user, question):
        existing = factories.VoteFactory(user=user, entry_id=question.id, value=-1)

        response = as_user.post(
            self.url.format(id=question.id, value=1),
        )

        assert response.status_code == 200

        store.refresh(existing)
        assert existing.value == 1

    def test_delete(self, store: Store, as_user, user, question):
        factories.VoteFactory(user=user, entry_id=question.id, value=1)

        response = as_user.post(
            self.url.format(id=question.id, value=0),
        )

        assert response.status_code == 200
        assert not repo.vote.exists(store, user_id=user.id, entry_id=question.id)

    def test_error(self, store: Store, as_user, user, question):
        response = as_user.post(
            self.url.format(id=question.id, value=5),
        )

        assert response.status_code == 400
        assert response.json == {"error": "Invalid vote value"}

        assert not repo.vote.exists(store, user_id=user.id, entry_id=question.id)


class TestDeleteEntry:
    url = "/entries/{id}"

    @pytest.mark.freeze_time("2030-01-01")
    def test_ok(self, store: Store, as_user, entry):
        response = as_user.delete(self.url.format(id=entry.id))

        assert response.status_code == 204

        store.refresh(entry)
        assert entry.deleted_at == datetime(2030, 1, 1)

    def test_unexisting_question(self, as_user):
        response = as_user.delete(self.url.format(id=999))

        assert response.status_code == 404

    def test_unauthorized(self, client, entry):
        response = client.delete(self.url.format(id=entry.id), follow_redirects=False)

        assert response.status_code == 302
        assert response.location.startswith(full_url_for("auth.login"))
