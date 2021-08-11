from datetime import datetime

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer

from db.base import Base


class View(Base):
    __tablename__ = "question_views"

    entry_id = Column(Integer, ForeignKey("entries.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
