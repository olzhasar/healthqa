import repository as repo
from storage import store


def update_question_search_index(question_id: int) -> None:
    from app.main import app

    with app.app_context():
        question = repo.question.get(store, question_id)
        repo.question.update_search_indexes(store, question)
