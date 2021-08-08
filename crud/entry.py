from sqlalchemy.orm import Session

from models import Entry


def exists(db: Session, *, id: int) -> bool:
    return bool(db.query(Entry.id).filter(Entry.id == id).first())
