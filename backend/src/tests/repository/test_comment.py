import pytest

import repository as repo
from repository import exceptions
from storage import Store

pytestmark = [pytest.mark.allow_db]


def test_get(store: Store, question_or_answer_comment, max_num_queries):
    with max_num_queries(1):
        assert (
            repo.comment.get(store, question_or_answer_comment.id)
            == question_or_answer_comment
        )


def test_get_for_user(
    store: Store, question_or_answer_comment, user, other_user, max_num_queries
):
    with max_num_queries(1):
        assert (
            repo.comment.get_for_user(
                store, id=question_or_answer_comment.id, user_id=user.id
            )
            == question_or_answer_comment
        )


def test_get_for_user_non_existing(store: Store, question_or_answer_comment, other_user):
    with pytest.raises(exceptions.NotFoundError):
        repo.comment.get_for_user(
            store, id=question_or_answer_comment.id, user_id=other_user.id
        )


def test_create(store: Store, user, question_or_answer):
    comment = repo.comment.create(
        store, user=user, entry_id=question_or_answer.id, content="Test content"
    )

    from_db = repo.comment.get(store, comment.id)

    assert from_db == comment
    assert from_db.entry_id == question_or_answer.id
    assert from_db.content == "Test content"


@pytest.mark.freeze_time("2030-01-01")
def test_update(store: Store, question_or_answer_comment):
    repo.comment.update(store, question_or_answer_comment, content="Updated content")

    store.db.refresh(question_or_answer_comment)

    assert question_or_answer_comment.content == "Updated content"
