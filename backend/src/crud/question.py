from typing import Optional

from redis import Redis
from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql.functions import func

from models import Comment, Question, Tag, User, Vote
from models.question import question_tags_table


def get(db: Session, *, id: int) -> Question:
    return (
        db.query(Question)
        .filter(
            Question.id == id,
            Question.deleted_at.is_(None),
        )
        .one()
    )


def get_with_related(
    db: Session, redis_db: Redis, *, id: int, user_id: int = 0
) -> Question:
    # TODO: load tags with question via join

    CommentUser = aliased(User)
    CommentVote = aliased(Vote)

    return with_count(
        db.query(Question)
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


def with_count(redis_db, question) -> list[Question]:
    question.view_count = get_view_count(redis_db, question_id=question.id)

    return question


def with_counts(redis_db, questions: list[Question]) -> list[Question]:
    ids = [q.id for q in questions]
    counts = get_view_count_list(redis_db, ids=ids)

    for i, question in enumerate(questions):
        question.view_count = counts[i]

    return questions


def get_list(
    db: Session,
    *,
    tag: Optional[Tag] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Question]:

    filter_params = [Question.deleted_at.is_(None)]
    if tag:
        filter_params.append(
            Question.tags.any(id=tag.id),
        )

    return (
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
        .filter(*filter_params)
        .order_by(Question.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_popular_list(
    db: Session, redis_db: Redis, *, limit: int = 20, offset: int = 0
) -> list[Question]:
    return with_counts(
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
        .filter(Question.deleted_at.is_(None))
        .order_by(Question.score.desc(), Question.answer_count.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def create(
    db: Session, *, user: User, title: str, content: str, tags: list[int]
) -> Question:
    question = Question(user=user, title=title, content=content)

    db.add(question)
    db.flush()

    if tags:
        tag_values = [(question.id, tag_id) for tag_id in tags]
        db.execute(question_tags_table.insert().values(tag_values))

    db.commit()

    return question


def update(
    db: Session, *, question: Question, new_title: str, new_content: str, tags: list[int]
) -> None:
    question.title = new_title
    question.content = new_content

    db.add(question)

    db.execute(
        question_tags_table.delete().where(
            question_tags_table.c.question_id == question.id
        )
    )

    if tags:
        tag_values = [(question.id, tag_id) for tag_id in tags]
        db.execute(question_tags_table.insert().values(tag_values))

    db.commit()


def count(db: Session, tag: Optional[Tag] = None) -> int:
    filter_params = [Question.deleted_at.is_(None)]
    if tag:
        filter_params.append(
            Question.tags.any(id=tag.id),
        )

    return db.query(func.count(Question.id)).filter(*filter_params).scalar()


def _clean_query(query: str):
    words = query.replace("\\", "").strip().split(" ")
    return "&".join(words)


def search(
    db: Session, *, query: str, limit: int = 20, offset: int = 0
) -> list[Question]:
    query = _clean_query(query)

    return (
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
        .filter(
            Question.deleted_at.is_(None),
            or_(Question.title.match(query), Question.content.match(query)),
        )
        .order_by(Question.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def search_count(db: Session, *, query: str) -> int:
    query = _clean_query(query)

    return (
        db.query(func.count(Question.id))
        .filter(
            Question.deleted_at.is_(None),
            or_(Question.title.match(query), Question.content.match(query)),
        )
        .scalar()
    )


def get_list_for_user(
    db: Session, *, user_id: int, limit: int = 10, offset: int = 0
) -> list[Question]:
    return (
        db.query(Question)
        .filter(Question.deleted_at.is_(None), Question.user_id == user_id)
        .order_by(Question.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def register_view(redis_db: Redis, *, question_id: int, ip_address: str):
    redis_db.pfadd(f"question:{question_id}:views", ip_address)


def get_view_count(redis_db: Redis, *, question_id) -> int:
    return redis_db.pfcount(f"question:{question_id}:views")


def get_view_count_list(redis_db: Redis, *, ids: list[int]) -> list[int]:
    pipe = redis_db.pipeline()
    for question_id in ids:
        pipe.pfcount(f"question:{question_id}:views")
    return pipe.execute()
