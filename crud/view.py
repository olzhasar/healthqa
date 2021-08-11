from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from models.entry import Entry
from models.view import View


def create(db: Session, *, entry_id: int, user_id: int) -> Optional[View]:
    view = View(entry_id=entry_id, user_id=user_id)
    try:
        db.add(view)
        db.flush()
    except IntegrityError:
        db.rollback()
        return None

    db.query(Entry).filter(Entry.id == entry_id).update(
        {"view_count": (Entry.view_count + 1)}
    )
    db.commit()

    return view
