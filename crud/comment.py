from sqlalchemy.orm import Session

from models import Comment, User


def get_for_user(db: Session, *, id: int, user_id: int) -> Comment:
    return db.query(Comment).filter(Comment.id == id, Comment.user_id == user_id).one()


def create(db: Session, *, user: User, entry_id: int, content: str):
    comment = Comment(
        user=user,
        entry_id=entry_id,
        content=content,
    )

    db.add(comment)
    db.commit()

    return comment


def update(db: Session, *, instance: Comment, content: str):
    instance.content = content

    db.add(instance)
    db.commit()
