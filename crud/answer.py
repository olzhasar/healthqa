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
