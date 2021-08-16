import pytest

from tests import factories


@pytest.fixture
def question_with_related(user):
    question = factories.QuestionFactory()

    factories.VoteFactory.create_batch(2, entry_id=question.id)
    factories.VoteFactory(entry_id=question.id, user=user)

    for comment in factories.CommentFactory.create_batch(2, entry_id=question.id):
        factories.VoteFactory.create_batch(2, entry_id=comment.id)
        factories.VoteFactory(entry_id=comment.id, user=user)

    for answer in factories.AnswerFactory.create_batch(2, question=question):
        factories.VoteFactory.create_batch(2, entry_id=answer.id)
        factories.VoteFactory(entry_id=answer.id, user=user)

        for comment in factories.CommentFactory.create_batch(2, entry_id=answer.id):
            factories.VoteFactory.create_batch(2, entry_id=comment.id)
            factories.VoteFactory(entry_id=comment.id, user=user)

    return question
