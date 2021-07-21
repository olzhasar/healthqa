from sqlalchemy.orm import Session

from models import Comment, User


def create_for_question(db: Session, *, user: User, question_id: int, content: str):
    comment = Comment(
        user=user,
        question_id=question_id,
        content=content,
    )

    db.add(comment)
    db.commit()

    return comment


def create_for_answer(db: Session, *, user: User, answer_id: int, content: str):
    comment = Comment(
        user=user,
        answer_id=answer_id,
        content=content,
    )

    db.add(comment)
    db.commit()

    return comment
