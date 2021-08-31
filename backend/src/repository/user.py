from sqlalchemy import exc

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

    def get_with_password():
        pass

    def create(self) -> User:
        pass
