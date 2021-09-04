from datetime import datetime

from flask.helpers import url_for
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import func
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
        "Question", back_populates="answers", foreign_keys=[question_id]
    )

    content = Column(Text)

    __mapper_args__ = {
        "polymorphic_identity": 2,
    }

    @property
    def url(self) -> str:
        return url_for("questions.details", id=self.question_id) + f"#answer_{self.id}"


Question.answer_count = column_property(  # type:ignore
    select(func.count("id"))
    .where(Answer.question_id == Question.id)
    .correlate_except(Answer)
    .scalar_subquery()
)
