import pytest

from tests import factories


class TestIndex:
    url = "/"

    @pytest.fixture(autouse=True)
    def data(self, db):
        tags = factories.TagFactory.create_batch(3)

        questions = factories.QuestionFactory.create_batch(2, tags=tags)

        for question in questions:
            factories.CommentFactory.create_batch(2, entry_id=question.id)
            factories.VoteFactory.create_batch(2, entry_id=question.id)

            for answer in factories.AnswerFactory.create_batch(2, question=question):
                factories.CommentFactory.create_batch(2, entry_id=answer.id)
                factories.VoteFactory.create_batch(2, entry_id=answer.id)

    def test_ok(self, client, max_num_queries, template_rendered):
        with max_num_queries(2):
            response = client.get(self.url)

        assert response.status_code == 200
        assert template_rendered("home/index.html")


class TestAbout:
    url = "/about"

    def test_ok(self, client, template_rendered):
        response = client.get(self.url)

        assert response.status_code == 200
        assert template_rendered("home/about.html")
