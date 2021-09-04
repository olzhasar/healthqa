from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import aliased, contains_eager
from sqlalchemy.sql.expression import and_

from models import Answer, Comment, Question, User, Vote
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from storage.base import Store


class AnswerRepostiory(BaseRepostitory[Answer]):
    def create(
        self, store: Store, *, user: User, question_id: int, content: str
    ) -> Answer:
        answer = Answer(
            user=user,
            question_id=question_id,
            content=content,
        )

        store.db.add(answer)
        store.db.commit()

        return answer

    def update(self, store: Store, *, answer: Answer, new_content: str) -> None:
        answer.content = new_content
        store.db.add(answer)
        store.db.commit()

    def all_for_user(self, store: Store, user: User) -> List[Answer]:
        return (
            store.db.query(Answer)
            .filter(Answer.user_id == user.id)
            .order_by(Answer.created_at.desc())
            .all()
        )

    def all_for_question(
        self, store: Store, *, question_id: int, user_id: int = 0
    ) -> List[Question]:
        CommentVote = aliased(Vote)
        CommentUser = aliased(User)

        return (
            store.db.query(Answer)
            .join(User, Answer.user_id == User.id)
            .outerjoin(Vote, and_(Vote.entry_id == Answer.id, Vote.user_id == user_id))
            .outerjoin(Comment, Comment.entry_id == Answer.id)
            .outerjoin(CommentUser, CommentUser.id == Comment.user_id)
            .outerjoin(
                CommentVote,
                and_(CommentVote.entry_id == Comment.id, CommentVote.user_id == user_id),
            )
            .options(
                contains_eager(Answer.user),
                contains_eager(Answer.user_vote),
                contains_eager(Answer.comments).contains_eager(
                    Comment.user.of_type(CommentUser)
                ),
                contains_eager(Answer.comments).contains_eager(
                    Comment.user_vote.of_type(CommentVote)
                ),
            )
            .filter(Answer.question_id == question_id, Answer.deleted_at.is_(None))
            .order_by(Answer.score.desc(), Answer.id.desc(), Comment.id)
            .all()
        )


answer = AnswerRepostiory()
