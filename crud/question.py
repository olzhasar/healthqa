from sqlalchemy.orm.session import Session

from models.question import Question, Tag
from models.user import User


def get_all(db: Session, *, limit: int = 10):
    return db.query(Question).limit(limit).all()


def create(db: Session, *, user: User, title: str, content: str, tags: list[Tag]):
    question = Question(
        user=user,
        title=title,
        content=content,
        tags=tags,
    )

    db.add(question)
    db.commit()

    return question
