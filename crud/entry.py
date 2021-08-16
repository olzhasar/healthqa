from datetime import datetime

from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.sql.expression import and_

from models import Entry, Vote


def exists(db: Session, *, id: int) -> bool:
    return bool(db.query(Entry.id).filter(Entry.id == id).first())


def get(db: Session, *, id: int) -> Entry:
    return db.query(Entry).filter(Entry.id == id).one()


def get_with_user_vote(db: Session, *, id: int, user_id: int) -> Entry:
    return (
        db.query(Entry)
        .outerjoin(Vote, and_(Entry.id == Vote.entry_id, Vote.user_id == user_id))
        .options(contains_eager(Entry.user_vote))
        .filter(Entry.id == id)
        .one()
    )


def get_score(db: Session, *, id: int) -> int:
    return db.query(Entry.score).filter(Entry.id == id).scalar()


def mark_as_deleted(db: Session, *, id: int, user_id: int):
    entry = db.query(Entry).filter(Entry.id == id, Entry.user_id == user_id).one()
    entry.deleted_at = datetime.utcnow()

    db.add(entry)
    db.commit()
