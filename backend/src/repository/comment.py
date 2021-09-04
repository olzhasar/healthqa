from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from sqlalchemy import exc

from models import Comment, User
from repository import exceptions
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class CommentRepostiory(BaseRepostitory[Comment]):
    def get_for_user(self, store: Store, *, id: int, user_id: int) -> Comment:
        try:
            return (
                store.db.query(Comment)
                .filter(Comment.id == id, Comment.user_id == user_id)
                .one()
            )
        except exc.NoResultFound:
            raise exceptions.NotFoundError

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
