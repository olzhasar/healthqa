from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from models import Comment, User
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class CommentRepostiory(BaseRepostitory[Comment]):
    def get_for_user(self, store: Store, *, id: int, user_id: int) -> Comment:
        query = store.db.query(Comment).filter(
            Comment.id == id, Comment.user_id == user_id
        )
        return self._get(store, query)

    def create(
        self, store: Store, *, user: User, entry_id: int, content: str
    ) -> Comment:
        comment = Comment(
            user=user,
            entry_id=entry_id,
            content=content,
        )

        store.db.add(comment)
        store.db.commit()

        return comment

    def update(self, store: Store, instance: Comment, *, content: str) -> NoReturn:
        instance.content = content

        store.db.add(instance)
        store.db.commit()


comment = CommentRepostiory()
