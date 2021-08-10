from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer

from db.base import Base
from models.user import User

if TYPE_CHECKING:
    from models.vote import Vote


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="entries")

    score = Column(Integer, nullable=False, default=0)

    votes: List["Vote"] = relationship("Vote")

    @property
    def user_vote(self):
        try:
            return self.votes[0]
        except (AttributeError, IndexError):
            return None

    __mapper_args__ = {
        "polymorphic_identity": 0,
        "polymorphic_on": type,
    }