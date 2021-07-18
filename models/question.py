from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import Integer, String, Text

from db.base import Base
from models.mixins import TimeStamped
from models.tag import Tag
from models.user import User

question_tags_table = Table(
    "question_tags",
    Base.metadata,
    Column(
        "question_id",
        Integer,
        ForeignKey("questions.id"),
        nullable=False,
        index=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id"),
        nullable=False,
        index=True,
    ),
)


class Question(TimeStamped, Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user: User = relationship("User", backref="questions")

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    tags: list[Tag] = relationship("Tag", secondary=question_tags_table)
