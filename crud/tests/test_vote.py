import crud
from tests import factories


def test_get_dict_for_user(db, user):
    expected = {}

    for question in factories.QuestionFactory.create_batch(3):
        vote = factories.VoteFactory(entry_id=question.id, user=user)
        expected[question.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=question.id)

    for answer in factories.AnswerFactory.create_batch(3):
        vote = factories.VoteFactory(entry_id=answer.id, user=user)
        expected[answer.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=answer.id)

    for comment in factories.CommentFactory.create_batch(3, entry_id=question.id):
        vote = factories.VoteFactory(entry_id=comment.id, user=user)
        expected[comment.id] = vote.value

        factories.VoteFactory.create_batch(2, entry_id=comment.id)

    result = crud.vote.get_dict_for_user(db, user_id=user.id)
    assert result == expected
