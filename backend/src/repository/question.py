from typing import Any, List, NoReturn

from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.sql.expression import and_, or_

from common.pagination import Paginator
from models import Comment, Question, User, Vote
from models.question import question_tags_table
from repository.base import BaseRepostitory
from storage import Store

PER_PAGE = 16


class QuestionRepository(BaseRepostitory[Question]):
    def get_with_related(self, store: Store, id: int, user_id: int = 0) -> Question:
        CommentUser = aliased(User)
        CommentVote = aliased(Vote)

        return (
            store.db.query(Question)
            .join(User, Question.user_id == User.id)
            .outerjoin(
                Vote,
                and_(Vote.entry_id == Question.id, Vote.user_id == user_id),
            )
            .outerjoin(
                Comment,
                and_(Comment.entry_id == Question.id, Comment.deleted_at.is_(None)),
            )
            .order_by(Comment.id)
            .outerjoin(
                CommentVote,
                and_(CommentVote.entry_id == Comment.id, CommentVote.user_id == user_id),
            )
            .outerjoin(CommentUser, Comment.user_id == CommentUser.id)
            .options(
                contains_eager(Question.user),
                contains_eager(Question.user_vote),
                contains_eager(Question.comments).contains_eager(
                    Comment.user.of_type(CommentUser)
                ),
                contains_eager(Question.comments).contains_eager(
                    Comment.user_vote.of_type(CommentVote)
                ),
            )
            .filter(Question.id == id, Question.deleted_at.is_(None))
            .one()
        )

    def create(
        self, store: Store, *, user: User, title: str, content: str, tags: List[int]
    ) -> Question:
        question = Question(user=user, title=title, content=content)

        store.db.add(question)
        store.db.flush()

        if tags:
            tag_values = [(question.id, tag_id) for tag_id in tags]
            store.db.execute(question_tags_table.insert().values(tag_values))

        store.db.commit()

        return question

    def update(
        self,
        store: Store,
        question: Question,
        *,
        new_title: str,
        new_content: str,
        tags: List[int]
    ) -> NoReturn:

        question.title = new_title
        question.content = new_content
        store.db.add(question)

        store.db.execute(
            question_tags_table.delete().where(
                question_tags_table.c.question_id == question.id
            )
        )

        if tags:
            tag_values = [(question.id, tag_id) for tag_id in tags]
            store.db.execute(question_tags_table.insert().values(tag_values))

        store.db.commit()

    def _list_default_ordering(self) -> List[Any]:
        return [Question.id.desc()]

    def _list_base_query(self, store: Store):
        return store.db.query(Question).options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )

    def _list_default_filters(self):
        return [Question.deleted_at.is_(None)]

    def list_for_user(
        self, store: Store, user: User, *, page: int = 1, per_page: int = PER_PAGE
    ) -> Paginator[Question]:

        filters = [Question.user_id == user.id]

        return self.list(store, page=page, per_page=per_page, filters=filters)

    @staticmethod
    def _clean_search_query(query: str):
        words = query.replace("\\", "").strip().split(" ")
        return "&".join(words)

    def search(
        self, store: Store, query: str, *, page: int = 1, per_page: int = PER_PAGE
    ) -> Paginator[Question]:
        query = self._clean_search_query(query)

        filters = [
            or_(Question.title.match(query), Question.content.match(query)),
        ]

        return self.list(store, page=page, per_page=per_page, filters=filters)


question = QuestionRepository()
