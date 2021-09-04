from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from models import Vote
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class VoteRepository(BaseRepostitory[Vote]):
    def get(self, store: Store, *, user_id: int, entry_id: int):
        query = store.db.query(Vote).filter(
            Vote.entry_id == entry_id, Vote.user_id == user_id
        )

        return self._get(store, query)

    def exists(self, store: Store, *, user_id: int, entry_id: int):
        return bool(
            store.db.query(Vote.id)
            .filter(Vote.entry_id == entry_id, Vote.user_id == user_id)
            .first()
        )

    def record(
        self, store: Store, *, user_id: int, entry_id: int, value: int
    ) -> Optional[Vote]:
        existing = (
            store.db.query(Vote)
            .filter(Vote.user_id == user_id, Vote.entry_id == entry_id)
            .one_or_none()
        )

        if value == 0:
            if not existing:
                raise ValueError("Vote does not exist")

            store.db.delete(existing)
            store.db.commit()
            return None

        if value not in [1, 2]:
            raise ValueError("Invalid vote value")

        if value == 2:
            value = -1

        if existing:
            if existing.value == value:
                raise ValueError("Vote already exists")

            existing.value = value
            store.db.add(existing)
            store.db.commit()
            return existing

        vote = Vote(user_id=user_id, entry_id=entry_id, value=value)
        store.db.add(vote)
        store.db.commit()
        return vote


vote = VoteRepository()
