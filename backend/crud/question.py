from typing import Optional

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


def get_with_related(db: Session, *, id: int, user_id: int = 0) -> Question:
    # TODO: load tags with question via join

    CommentUser = aliased(User)
    CommentVote = aliased(Vote)

    return (
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


def get_list(
    db: Session, *, tag: Optional[Tag] = None, limit: int = 20, offset: int = 0
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


def get_popular_list(db: Session, *, limit: int = 20, offset: int = 0) -> list[Question]:
    return (
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
    words = query.strip().split(" ")
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
