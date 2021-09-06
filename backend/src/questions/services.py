from typing import List

import repository as repo
from models import Question, User
from questions.tasks import update_question_search_index
from storage.base import Store
from worker import queue


def create_question(
    store: Store, *, user: User, title: str, content: str, tags: List[int]
) -> Question:
    question = repo.question.create(
        store, user=user, title=title, content=content, tags=tags
    )

    queue.enqueue(update_question_search_index, question_id=question.id)

    return question


def update_question(
    store: Store,
    question: Question,
    *,
    new_title: str,
    new_content: str,
    tags: List[int]
) -> Question:
    repo.question.update(
        store, question, new_title=new_title, new_content=new_content, tags=tags
    )

    queue.enqueue(update_question_search_index, question_id=question.id)

    return question
