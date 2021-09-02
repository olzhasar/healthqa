from sqlalchemy import exc

from auth.security import hash_password
from common.pagination import Paginator
from models.user import User
from repository import exceptions
from repository.base import BaseRepostitory


class UserRepository(BaseRepostitory):
    def get(self, id: int) -> User:
        try:
            return self.db.query(User).filter(User.id == id).one()
        except exc.NoResultFound:
            raise exceptions.NotFoundError

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

        try:
            with self.db.begin():
                self.db.add(user)
        except exc.IntegrityError:
            raise exceptions.AlreadyExistsError(
                "User with this email is already registered"
            )

        return user

    def change_password(self, user: User, new_password: str):
        user.password = hash_password(new_password)

        with self.db.begin():
            self.db.add(user)

    def reset_password(self, user: User):
        user.password = None

        with self.db.begin():
            self.db.add(user)

    def update_info(self, user: User, *, name: str):
        user.name = name

        with self.db.begin():
            self.db.add(user)

    def mark_email_verified(self, user: User):
        user.email_verified = True

        with self.db.begin():
            self.db.add(user)
