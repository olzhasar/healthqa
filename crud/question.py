from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session

from models import Answer, Comment, Question, Tag, User


def get_by_id(db: Session, id: int):
    return db.query(Question).filter(Question.id == id).first()


def get_for_view(db: Session, id: int):
    return (
        db.query(Question)
        .filter(Question.id == id)
        .options(
            joinedload(Question.tags),
            joinedload(Question.user).load_only("id", "name"),
            joinedload(Question.comments).options(
                joinedload(Comment.user).load_only("id", "name")
            ),
            joinedload(Question.answers).options(
                joinedload(Answer.user).load_only("id", "name"),
                joinedload(Answer.comments).options(joinedload(Comment.user)),
            ),
        )
        .first()
    )


def get_all(db: Session, *, limit: int = 10):
    return (
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
        .order_by(Question.id.desc())
        .limit(limit)
        .all()
    )


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
