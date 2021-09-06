from unittest.mock import MagicMock

import pytest

from questions import services, tasks
from storage.base import Store


@pytest.mark.allow_db
def test_create_question(store: Store, mock_enqueue: MagicMock, user):
    data = {
        "user": user,
        "title": "Test title",
        "content": "Test content",
        "tags": [],
    }

    question = services.create_question(store, **data)
    store.refresh(question)

    assert question.user == user
    assert question.title == data["title"]
    assert question.content == data["content"]
    assert question.tags == data["tags"]

    mock_enqueue.assert_called_once_with(
        tasks.update_question_search_index, question_id=question.id
    )


@pytest.mark.allow_db
def test_update_question(store: Store, question, mock_enqueue: MagicMock, user):
    data = {
        "new_title": "Test title",
        "new_content": "Test content",
        "tags": [],
    }

    services.update_question(store, question, **data)

    store.refresh(question)

    assert question.title == data["new_title"]
    assert question.content == data["new_content"]
    assert question.tags == data["tags"]

    mock_enqueue.assert_called_once_with(
        tasks.update_question_search_index, question_id=question.id
    )
