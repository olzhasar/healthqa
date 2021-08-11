from sqlalchemy.orm.session import Session

import crud
from models.question import Question
from models.view import View


def test_create(db: Session, question, user):
    crud.view.create(db, entry_id=question.id, user_id=user.id)

    assert bool(
        db.query(View.entry_id)
        .filter(View.entry_id == question.id, View.user_id == user.id)
        .first()
    )
    assert db.query(Question.view_count).filter(Question.id == question.id).scalar() == 1

    crud.view.create(db, entry_id=question.id, user_id=user.id)
    assert db.query(Question.view_count).filter(Question.id == question.id).scalar() == 1
