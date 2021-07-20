from sqlalchemy import Column, Integer, String

from db.base import Base
from models.mixins import TimeStamped


class User(TimeStamped, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(100))

    @property
    def is_authenticated(self) -> bool:
        return bool(self.id)

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return not self.is_authenticated

    def get_id(self) -> str:
        return str(self.id)
