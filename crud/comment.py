from sqlalchemy.orm import Session

from models import Comment, User


def create(db: Session, *, user: User, entry_id: int, content: str):
    comment = Comment(
        user=user,
        entry_id=entry_id,
        content=content,
    )

    db.add(comment)
    db.commit()

    return comment
