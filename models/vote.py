from datetime import datetime

from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, Integer, SmallInteger

from db.base import Base
from models.entry import Entry
from models.user import User


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    created_at = deferred(Column(DateTime, nullable=False, default=datetime.utcnow))

    user_id = deferred(
        Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    )
    user: User = relationship("User", backref="votes")

    entry_id = deferred(
        Column(
            Integer,
            ForeignKey("entries.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    entry: Entry = relationship("Entry", back_populates="votes", foreign_keys=[entry_id])

    value = Column(SmallInteger, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "entry_id", name="user_entry_uc"),)
