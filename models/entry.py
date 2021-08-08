from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer

from db.base import Base
from models.mixins import TimeStamped
from models.user import User


class Entry(TimeStamped, Base):
    __tablename__ = "entries"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="entries")

    score = Column(Integer, nullable=False, default=0)

    __mapper_args__ = {
        "polymorphic_identity": 0,
        "polymorphic_on": type,
    }
