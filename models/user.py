from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import deferred, query_expression
from sqlalchemy.sql.sqltypes import DateTime

from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    created_at = deferred(Column(DateTime, nullable=False, default=datetime.utcnow))
    modified_at = deferred(
        Column(
            DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
        )
    )

    email = Column(String(255), nullable=False, unique=True, index=True)
    password = deferred(Column(String(100)))
    name = Column(String(100), nullable=False)

    question_count: int = query_expression()
    answer_count: int = query_expression()
    comment_count: int = query_expression()

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
