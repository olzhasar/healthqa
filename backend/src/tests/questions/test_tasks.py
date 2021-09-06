from unittest.mock import MagicMock

import pytest

import repository as repo
from questions import tasks


@pytest.mark.allow_db
def test_update_question_search_index(question, meili_client_mock: MagicMock):
    tasks.update_question_search_index(question.id)

    doc = repo.question._build_meili_document(question)

    meili_client_mock.index("questions").add_documents.assert_called_once_with([doc])
