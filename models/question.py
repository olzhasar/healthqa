from datetime import datetime
from typing import TYPE_CHECKING

from flask import url_for
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey, Table
from sqlalchemy.sql.sqltypes import DateTime, Integer, String, Text

from db.base import Base
from models.entry import Entry
from models.tag import Tag

if TYPE_CHECKING:
    from models.answer import Answer


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


class Question(Entry):
    __tablename__ = "questions"

    id = Column(Integer, ForeignKey("entries.id"), primary_key=True)

    edited_at = Column(DateTime, onupdate=datetime.utcnow)

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    tags: list[Tag] = relationship("Tag", secondary=question_tags_table)
    answers: list["Answer"] = relationship(
        "Answer", back_populates="question", foreign_keys="Answer.question_id"
    )

    answer_count: int

    __mapper_args__ = {
        "polymorphic_identity": 1,
    }

    @property
    def url(self):
        return url_for("questions.details", id=self.id)
