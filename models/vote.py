from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, SmallInteger

from models.user_action import UserAction


class Vote(UserAction):
    __tablename__ = "votes"

    id = Column(Integer, ForeignKey("user_actions.id"), primary_key=True)

    user_action_id = Column(
        Integer,
        ForeignKey("user_actions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_action: UserAction = relationship(
        "UserAction", backref="votes", foreign_keys=[user_action_id]
    )
    value = Column(SmallInteger, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": 4,
        "inherit_condition": id == UserAction.id,
    }
