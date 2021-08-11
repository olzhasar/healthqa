from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, Text

from models.entry import Entry


class Comment(Entry):
    __tablename__ = "comments"

    id = Column(Integer, ForeignKey("entries.id"), primary_key=True)

    edited_at = Column(DateTime, onupdate=datetime.utcnow)

    entry_id = Column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry: Entry = relationship(
        "Entry", back_populates="comments", foreign_keys=[entry_id]
    )

    content = Column(Text, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": 3,
        "inherit_condition": id == Entry.id,
    }
