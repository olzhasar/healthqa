from sqlalchemy.orm import Session

from models import Answer, User


def get(db: Session, *, id: int) -> Answer:
    return db.query(Answer).filter(Answer.id == id).one()


def update(db: Session, *, answer: Answer, new_content: str) -> None:
    answer.content = new_content
    db.add(answer)
    db.commit()


def create(db: Session, *, user: User, question_id: int, content: str) -> Answer:
    answer = Answer(
        user=user,
        question_id=question_id,
        content=content,
    )

    db.add(answer)
    db.commit()

    return answer


def get_list_for_user(
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
