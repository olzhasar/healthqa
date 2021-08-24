from typing import Optional

from sqlalchemy.orm.session import Session

from models.entry import Entry
from models.view import View


def exists(db: Session, *, entry_id: int, user_id: int) -> bool:
    return db.query(
        db.query(View)
        .filter(View.entry_id == entry_id, View.user_id == user_id)
        .exists()
    ).scalar()


def create(db: Session, *, entry_id: int, user_id: int) -> Optional[View]:
    if exists(db, entry_id=entry_id, user_id=user_id):
        return None

    view = View(entry_id=entry_id, user_id=user_id)
    db.add(view)

    db.query(Entry).filter(Entry.id == entry_id).update(
        {"view_count": (Entry.view_count + 1)}
    )
    db.commit()

    return view
