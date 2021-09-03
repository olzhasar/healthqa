from sqlalchemy import exc
from sqlalchemy.orm import undefer

from auth.security import hash_password
from common.pagination import Paginator
from models.user import User
from repository import exceptions
from repository.base import BaseRepostitory


class UserRepository(BaseRepostitory):
    def get(self, id: int, *options, **filter_kwargs) -> User:
        try:
            return (
                self.db.query(User)
                .filter(User.id == id, **filter_kwargs)
                .options(*options)
                .one()
            )
        except exc.NoResultFound:
            raise exceptions.NotFoundError

    def get_with_password(self, id: int) -> User:
        return self.get(id, undefer("password"))

    def get_by_email(self, email: str) -> User:
        try:
            return self.db.query(User).filter(User.email == email).one()
        except exc.NoResultFound:
            raise exceptions.NotFoundError

    def count(self) -> int:
        return self.db.query(User.id).count()

    def list(self, *, page: int = 1, per_page: int = 16) -> Paginator[User]:
        total = self.count()
        offset = Paginator.calc_offset(page, per_page)

        objects = self.db.query(User).limit(per_page).offset(offset).all()

        return Paginator(objects=objects, total=total, page=page, per_page=per_page)

    def create(self, *, email: str, name: str, password: str) -> User:
        hashed_password = hash_password(password)
        user = User(email=email, name=name, password=hashed_password)

        self.db.add(user)
        try:
            self.db.flush()
        except exc.IntegrityError:
            self.db.rollback()
            raise exceptions.AlreadyExistsError(
                "User with this email is already registered"
            )
        else:
            self.db.commit()

        return user

    def change_password(self, user: User, new_password: str):
        user.password = hash_password(new_password)

        self.db.add(user)
        self.db.commit()

    def reset_password(self, user: User):
        user.password = None

        self.db.add(user)
        self.db.commit()

    def update_info(self, user: User, *, name: str):
        user.name = name

        self.db.add(user)
        self.db.commit()

    def mark_email_verified(self, user: User):
        user.email_verified = True

        self.db.add(user)
        self.db.commit()
