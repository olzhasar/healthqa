from typing import Optional

from sqlalchemy.orm.session import Session

from models.vote import Vote


def record(db: Session, *, user_id: int, entry_id: int, value: int) -> Optional[Vote]:
    existing = (
        db.query(Vote)
        .filter(Vote.user_id == user_id, Vote.entry_id == entry_id)
        .one_or_none()
    )

    if value == 0:
        if not existing:
            raise ValueError("Vote does not exist")

        db.delete(existing)
        db.commit()
        return None

    if value not in [1, 2]:
        raise ValueError("Invalid vote value")

    if value == 2:
        value = -1

    if existing:
        if existing.value == value:
            raise ValueError("Vote already exists")

        existing.value = value
        db.add(existing)
        db.commit()
        return existing

    vote = Vote(user_id=user_id, entry_id=entry_id, value=value)
    db.add(vote)
    db.commit()
    return vote
