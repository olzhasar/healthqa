import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

import crud
from models.comment import Comment


def test_get_for_user(db: Session, question_or_answer_comment, user, other_user):
    comment = crud.comment.get_for_user(
        db, id=question_or_answer_comment.id, user_id=user.id
    )

    assert comment == question_or_answer_comment

    with pytest.raises(NoResultFound):
        crud.comment.get_for_user(
            db, id=question_or_answer_comment.id, user_id=other_user.id
        )


def test_create(db: Session, user, question_or_answer):
    comment = crud.comment.create(
        db, user=user, entry_id=question_or_answer.id, content="Test content"
    )

    from_db = db.query(Comment).filter(Comment.user_id == user.id).one()

    assert from_db == comment
    assert from_db.entry_id == question_or_answer.id
    assert from_db.content == "Test content"


@pytest.mark.freeze_time("2030-01-01")
def test_update(db: Session, question_or_answer_comment):
    crud.comment.update(
        db, instance=question_or_answer_comment, content="Updated content"
    )

    db.refresh(question_or_answer_comment)

    assert question_or_answer_comment.content == "Updated content"
