from collections import defaultdict
from typing import Optional

from sqlalchemy.orm.session import Session

from models.vote import Vote


def one_or_none(db: Session, *, user_id: int, entry_id: int) -> Optional[Vote]:
    return (
        db.query(Vote)
        .filter(Vote.user_id == user_id, Vote.entry_id == entry_id)
        .one_or_none()
    )


def get_dict_for_user(db: Session, *, user_id: int):
    result = defaultdict(lambda: 0)

    votes = db.query(Vote.entry_id, Vote.value).filter(Vote.user_id == user_id).all()

    for action_id, value in votes:
        result[action_id] = value

    return result


def delete(db: Session, *, user_id: int, entry_id: int) -> None:
    db.query(Vote).filter(Vote.user_id == user_id, Vote.entry_id == entry_id).delete()
    db.commit()


def create(db: Session, *, user_id: int, entry_id: int, value: int) -> Vote:
    vote = Vote(user_id=user_id, entry_id=entry_id, value=value)

    db.add(vote)
    db.commit()

    return vote
