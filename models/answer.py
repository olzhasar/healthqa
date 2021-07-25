from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from models.entity import UserAction
from models.question import Question


class Answer(UserAction):
    __tablename__ = "answers"

    id = Column(Integer, ForeignKey("user_actions.id"), primary_key=True)

    edited_at = Column(DateTime, onupdate=datetime.utcnow)

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    question: Question = relationship("Question", backref="answers")

    content = Column(Text)

    __mapper_args__ = {
        "polymorphic_identity": 2,
    }
