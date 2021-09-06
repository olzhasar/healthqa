import repository as repo
from storage import Store


def update_question_search_index(question_id: int) -> None:
    store = Store()
    question = repo.question.get(store, question_id)
    repo.question.update_search_indexes(store, question)
