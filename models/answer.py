from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text

from db.base import Base
from models.mixins import BaseVote, TimeStamped
from models.question import Question
from models.user import User


class Answer(TimeStamped, Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)

    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    question: Question = relationship("Question", backref="answers")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="answers")

    content = Column(Text)


class AnswerVote(BaseVote, Base):
    __tablename__ = "answer_votes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "answer_id",
            name="user_answer_uc",
        ),
    )

    answer_id = Column(
        Integer,
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer: Answer = relationship("Answer", backref="votes")

    user: User = relationship("User", backref="answer_votes")
