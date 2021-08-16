from sqlalchemy.orm import Session, aliased, contains_eager
from sqlalchemy.sql.expression import and_

from models import Answer, Comment, User, Vote


def get(db: Session, *, id: int) -> Answer:
    return db.query(Answer).filter(Answer.id == id).one()


def update(db: Session, *, answer: Answer, new_content: str) -> None:
    answer.content = new_content
    db.add(answer)
    db.commit()


def create(db: Session, *, user: User, question_id: int, content: str) -> Answer:
    answer = Answer(
        user=user,
        question_id=question_id,
        content=content,
    )

    db.add(answer)
    db.commit()

    return answer


def get_list_for_user(
    db: Session, *, user_id: int, limit: int = 10, offset: int = 0
) -> list[Answer]:
    return (
        db.query(Answer)
        .filter(Answer.user_id == user_id)
        .order_by(Answer.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_list_for_question(
    db: Session, *, question_id: int, user_id: int = 0
) -> list[Answer]:
    CommentVote = aliased(Vote)
    CommentUser = aliased(User)

    return (
        db.query(Answer)
        .join(User, Answer.user_id == User.id)
        .outerjoin(Vote, and_(Vote.entry_id == Answer.id, Vote.user_id == user_id))
        .outerjoin(Comment, Comment.entry_id == Answer.id)
        .order_by(Comment.id)
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
        .filter(Answer.question_id == question_id)
        .order_by(Answer.created_at.desc())
        .all()
    )
