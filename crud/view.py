from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from models.entry import Entry
from models.view import View


def create(db: Session, *, entry_id: int, user_id: int) -> Optional[View]:
    view = View(entry_id=entry_id, user_id=user_id)
    db.add(view)

    db.query(Entry).filter(Entry.id == entry_id).update(
        {"view_count": (Entry.view_count + 1)}
    )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    return view
