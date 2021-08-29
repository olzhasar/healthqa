from sqlalchemy.orm.session import Session

import crud
from models.question import Question
from models.view import View


class TestCreate:
    def test_ok(self, db: Session, question, user, other_user):
        crud.view.create(db, entry_id=question.id, user_id=user.id)

        assert bool(
            db.query(View.entry_id)
            .filter(View.entry_id == question.id, View.user_id == user.id)
            .first()
        )
        assert (
            db.query(Question.view_count).filter(Question.id == question.id).scalar()
            == 1
        )

        crud.view.create(db, entry_id=question.id, user_id=other_user.id)

        assert bool(
            db.query(View.entry_id)
            .filter(View.entry_id == question.id, View.user_id == other_user.id)
            .first()
        )
        assert (
            db.query(Question.view_count).filter(Question.id == question.id).scalar()
            == 2
        )

    def test_duplicate(self, db: Session, question, user):
        crud.view.create(db, entry_id=question.id, user_id=user.id)

        assert (
            db.query(Question.view_count).filter(Question.id == question.id).scalar()
            == 1
        )

        crud.view.create(db, entry_id=question.id, user_id=user.id)

        assert (
            db.query(Question.view_count).filter(Question.id == question.id).scalar()
            == 1
        )
