from sqlalchemy.orm import Session

from models import Entry


def exists(db: Session, *, id: int) -> bool:
    return bool(db.query(Entry.id).filter(Entry.id == id).first())


def get(db: Session, *, id: int) -> Entry:
    return db.query(Entry).filter(Entry.id == id).one()


def get_score(db: Session, *, id: int) -> int:
    return db.query(Entry.score).filter(Entry.id == id).scalar()
