from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text

from db.base import Base
from models.mixins import TimeStamped
from models.question import Question
from models.user import User


class Answer(TimeStamped, Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)

    question_id = Column(Integer, ForeignKey("questions.id"))
    question: Question = relationship("Question", backref="answers")

    user_id = Column(Integer, ForeignKey("users.id"))
    user: User = relationship("User", backref="answers")

    content = Column(Text)
