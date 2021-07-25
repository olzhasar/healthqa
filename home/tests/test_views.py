import pytest

from tests import factories


class TestIndex:
    url = "/"

    @pytest.fixture(autouse=True)
    def data(self, db):
        tags = factories.TagFactory.create_batch(3)

        questions = factories.QuestionFactory.create_batch(2, tags=tags)

        for question in questions:
            factories.CommentFactory.create_batch(2, user_action_id=question.id)
            factories.VoteFactory.create_batch(2, user_action_id=question.id)

            for answer in factories.AnswerFactory.create_batch(2, question=question):
                factories.CommentFactory.create_batch(2, user_action_id=answer.id)
                factories.VoteFactory.create_batch(2, user_action_id=answer.id)

    def test_ok(self, client, max_num_queries):
        with max_num_queries(2):
            response = client.get(self.url)

        assert response.status_code == 200
