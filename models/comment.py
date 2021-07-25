from datetime import datetime

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from models.entity import UserAction


class Comment(UserAction):
    __tablename__ = "comments"

    id = Column(Integer, ForeignKey("user_actions.id"), primary_key=True)

    edited_at = Column(DateTime, onupdate=datetime.utcnow)

    user_action_id = Column(
        Integer,
        ForeignKey("user_actions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": 3,
    }
