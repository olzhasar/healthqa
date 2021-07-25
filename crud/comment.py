from sqlalchemy.orm import Session

from models import Comment, User


def create(db: Session, *, user: User, user_action_id: int, content: str):
    comment = Comment(
        user=user,
        user_action_id=user_action_id,
        content=content,
    )

    db.add(comment)
    db.commit()

    return comment
