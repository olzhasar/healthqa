from typing import NoReturn

from sqlalchemy import exc
from sqlalchemy.orm import undefer

from auth.security import hash_password
from models.user import User
from repository import exceptions
from repository.base import BaseRepostitory
from storage.base import Store


class UserRepository(BaseRepostitory[User]):
    def first_with_password(self, store: Store, id: int) -> User:
        return (
            store.db.query(User)
            .options(undefer("password"))
            .filter(User.id == id)
            .first()
        )

    def get_by_email(self, store: Store, email: str) -> User:
        try:
            return store.db.query(User).filter(User.email == email).one()
        except exc.NoResultFound:
            raise exceptions.NotFoundError

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

    def change_password(self, store: Store, user: User, new_password: str) -> NoReturn:
        user.password = hash_password(new_password)

        store.db.add(user)
        store.db.commit()

    def reset_password(self, store: Store, user: User) -> NoReturn:
        user.password = None

        store.db.add(user)
        store.db.commit()

    def update_info(self, store: Store, user: User, *, name: str) -> NoReturn:
        user.name = name

        store.db.add(user)
        store.db.commit()

    def mark_email_verified(self, store: Store, user: User) -> NoReturn:
        user.email_verified = True

        store.db.add(user)
        store.db.commit()


user = UserRepository()
