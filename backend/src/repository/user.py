from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import exc
from sqlalchemy.orm import undefer, with_expression
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select, true
from sqlalchemy.sql.functions import func

from auth.security import hash_password
from models import Entry, User
from repository import exceptions
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


question_count = (
    select(func.count(Entry.id))
    .where(and_(Entry.user_id == User.id, Entry.type == 1))
    .scalar_subquery()
)
answer_count = (
    select(func.count(Entry.id))
    .where(and_(Entry.user_id == User.id, Entry.type == 2))
    .scalar_subquery()
)


class UserRepository(BaseRepostitory[User]):
    def first_with_password(self, store: Store, id: int) -> Optional[User]:
        return (
            store.db.query(User)
            .options(undefer("password"))
            .filter(User.id == id)
            .first()
        )

    def get_by_email(self, store: Store, email: str) -> User:
        query = store.db.query(User).filter(User.email == email)
        return self._get(query)

    def get_with_counts(self, store: Store, id: int) -> User:
        query = (
            store.db.query(User)
            .options(
                with_expression(User.question_count, question_count),
                with_expression(User.answer_count, answer_count),
            )
            .filter(User.id == id)
        )
        return self._get(query)

    def _list_default_filters(self) -> List[Any]:
        return [User.email_verified == true()]

    def _list_default_ordering(self) -> List[Any]:
        return [User.created_at]

    def _list_base_query(self, store: Store) -> Query:
        return store.db.query(User).options(
            with_expression(User.question_count, question_count),
            with_expression(User.answer_count, answer_count),
        )

    def create(self, store: Store, *, email: str, name: str, password: str) -> User:
        hashed_password = hash_password(password)
        user = User(email=email, name=name, password=hashed_password)

        store.db.add(user)
        try:
            store.db.flush()
        except exc.IntegrityError:
            store.db.rollback()
            raise exceptions.AlreadyExistsError(
                "User with this email is already registered"
            )
        else:
            store.db.commit()

        return user

    def change_password(self, store: Store, user: User, new_password: str) -> None:
        user.password = hash_password(new_password)

        store.db.add(user)
        store.db.commit()

    def reset_password(self, store: Store, user: User) -> None:
        user.password = None

        store.db.add(user)
        store.db.commit()

    def update_info(self, store: Store, user: User, *, name: str) -> None:
        user.name = name

        store.db.add(user)
        store.db.commit()

    def mark_email_verified(self, store: Store, user: User) -> None:
        user.email_verified = True

        store.db.add(user)
        store.db.commit()


user = UserRepository()
