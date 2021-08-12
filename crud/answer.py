from sqlalchemy.orm import Session

from models import Answer, User


def create(db: Session, *, user: User, question_id: int, content: str):
    answer = Answer(
        user=user,
        question_id=question_id,
        content=content,
    )

    db.add(answer)
    db.commit()

    return answer


def list_for_user(
    db: Session, *, user_id: int, limit: int = 10, offset: int = 0
) -> list[Answer]:
    return (
        db.query(Answer)
        .filter(Answer.user_id == user_id)
        .order_by(Answer.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
