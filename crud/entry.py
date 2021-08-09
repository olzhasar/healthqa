from sqlalchemy.orm import Session

from models import Entry


def exists(db: Session, *, id: int) -> bool:
    return bool(db.query(Entry.id).filter(Entry.id == id).first())


def get_score(db: Session, *, id: int) -> int:
    return db.query(Entry.score).filter(Entry.id == id).scalar()
