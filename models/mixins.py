from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import declared_attr
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, SmallInteger

if TYPE_CHECKING:
    from models.user import User


class TimeStamped:
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Scored:
    score = Column(Integer, nullable=False, index=True, default=0)


class BaseVote:
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)

    score = Column(SmallInteger, nullable=False)

    @declared_attr
    def user_id(cls) -> Column[Integer]:
        return Column(
            Integer,
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=False,
            index=True,
        )

    @declared_attr
    def user(cls) -> relationship[User]:
        return relationship("User", backref="votes")
