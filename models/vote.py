from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, SmallInteger

from db.base import Base
from models.entry import Entry
from models.user import User


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="votes")

    entry_id = Column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry: Entry = relationship("Entry", backref="votes", foreign_keys=[entry_id])

    value = Column(SmallInteger, nullable=False)
