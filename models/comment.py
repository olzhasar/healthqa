from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Text

from db.base import Base
from models.answer import Answer
from models.mixins import BaseVote, TimeStamped
from models.question import Question
from models.user import User


class Comment(TimeStamped, Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="comments")

    question_id = Column(Integer, ForeignKey("questions.id"))
    question: Question = relationship("Question", backref="comments")

    answer_id = Column(Integer, ForeignKey("answers.id"))
    answer: Answer = relationship("Answer", backref="comments")

    content = Column(Text, nullable=False)


class CommentVote(BaseVote, Base):
    __tablename__ = "comment_votes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "comment_id",
            name="user_comment_uc",
        ),
    )

    comment_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment: Comment = relationship("Comment", backref="votes")

    user: User = relationship("User", backref="comment_votes")
