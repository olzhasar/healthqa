from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from models.entry import Entry
from models.question import Question


class Answer(Entry):
    __tablename__ = "answers"

    id = Column(Integer, ForeignKey("entries.id"), primary_key=True)

    edited_at = Column(DateTime, onupdate=datetime.utcnow)

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    question: Question = relationship(
        "Question", backref="answers", foreign_keys=[question_id]
    )

    content = Column(Text)

    __mapper_args__ = {
        "polymorphic_identity": 2,
    }
