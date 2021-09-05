from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.sql.expression import and_, or_

from common.pagination import Paginator
from models import Comment, Question, Tag, User, Vote
from models.question import question_tags_table
from repository.base import BaseRepostitory

if TYPE_CHECKING:
    from sqlalchemy.orm.query import Query

    from storage import Store

PER_PAGE = 16


class QuestionRepository(BaseRepostitory[Question]):
    REDIS_QUESTION_VIEW_KEY = "question:{id}:views"

    def get_with_related(self, store: Store, id: int, user_id: int = 0) -> Question:
        CommentUser = aliased(User)
        CommentVote = aliased(Vote)

        query = (
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
        )

        question = self._get(query)
        question.view_count = self.get_view_count(store, question.id)

        return question

    def first_for_user(self, store: Store, user: User) -> Optional[Question]:
        return store.db.query(Question).filter(Question.user_id == user.id).first()

    def get_view_count(self, store: Store, id: int) -> int:
        return store.redis.pfcount(self.REDIS_QUESTION_VIEW_KEY.format(id=id))

    def register_view(self, store: Store, id: int, user_identifier: str) -> None:
        store.redis.pfadd(self.REDIS_QUESTION_VIEW_KEY.format(id=id), user_identifier)

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
        tags: List[int],
    ) -> None:

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

    def _list_base_query(self, store: Store) -> Query:
        return store.db.query(Question).options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )

    def _list_default_filters(self) -> List[Any]:
        return [Question.deleted_at.is_(None)]

    def _with_view_counts(
        self, store: Store, questions: List[Question]
    ) -> List[Question]:
        pipe = store.redis.pipeline()
        for question in questions:
            _key = self.REDIS_QUESTION_VIEW_KEY.format(id=question.id)
            pipe.pfcount(_key)

        counts = pipe.execute()

        for question, c in zip(questions, counts):
            question.view_count = c

        return questions

    def all(
        self,
        store: Store,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: List[Any] = None,
        filters: List[Any] = None,
    ) -> List[Question]:

        questions = super().all(
            store, limit=limit, offset=offset, order_by=order_by, filters=filters
        )

        return self._with_view_counts(store, questions)

    def all_for_user(self, store: Store, user: User) -> List[Question]:
        return self.all(store, filters=[Question.user_id == user.id])

    def list_for_user(
        self, store: Store, user: User, *, page: int = 1, per_page: int = PER_PAGE
    ) -> Paginator[Question]:

        filters = [Question.user_id == user.id]

        return self.list(store, page=page, per_page=per_page, filters=filters)

    def list_by_tag(
        self, store: Store, tag: Tag, *, page: int = 1, per_page: int = PER_PAGE
    ) -> Paginator[Question]:

        filters = [Question.tags.any(id=tag.id)]

        return self.list(store, page=page, per_page=per_page, filters=filters)

    @staticmethod
    def _clean_search_query(query: str) -> str:
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
