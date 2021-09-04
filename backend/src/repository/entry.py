from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import exc
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.expression import and_

from models import Entry, Vote
from repository import exceptions
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class EntryRepository(BaseRepostitory[Entry]):
    def get_with_user_vote(self, store: Store, *, id: int, user_id: int) -> Entry:
        query = (
            store.db.query(Entry)
            .outerjoin(Vote, and_(Entry.id == Vote.entry_id, Vote.user_id == user_id))
            .options(contains_eager(Entry.user_vote))
            .filter(Entry.id == id)
        )

        return self._get(store, query)

    def get_score(self, store: Store, *, id: int) -> int:
        return store.db.query(Entry.score).filter(Entry.id == id).scalar()

    def mark_as_deleted(self, store: Store, *, id: int, user_id: int):
        try:
            entry = (
                store.db.query(Entry)
                .filter(Entry.id == id, Entry.user_id == user_id)
                .one()
            )
        except exc.NoResultFound:
            raise exceptions.NotFoundError

        entry.deleted_at = datetime.utcnow()

        store.db.add(entry)
        store.db.commit()


entry = EntryRepository()
