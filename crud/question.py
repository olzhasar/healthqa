from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.functions import func

from models import Answer, Comment, Question, Tag, User, Vote


def get_by_id(db: Session, id: int) -> Question:
    return db.query(Question).filter(Question.id == id).one()


def get_for_view(db: Session, *, id: int, user_id: int = 0) -> Question:
    AnswerComment = aliased(Comment)
    AnswerUser = aliased(User)
    CommentUser = aliased(User)
    AnswerCommentUser = aliased(User)
    QuestionVote = aliased(Vote)
    AnswerVote = aliased(Vote)
    CommentVote = aliased(Vote)
    AnswerCommentVote = aliased(Vote)

    return (
        db.query(Question)
        .join(User, Question.user_id == User.id)
        .outerjoin(
            QuestionVote,
            and_(Question.id == QuestionVote.entry_id, QuestionVote.user_id == user_id),
        )
        .outerjoin(Answer, Question.id == Answer.question_id)
        .order_by(Answer.score.desc())
        .outerjoin(AnswerUser, Answer.user_id == AnswerUser.id)
        .outerjoin(
            AnswerVote,
            and_(Answer.id == AnswerVote.entry_id, AnswerVote.user_id == user_id),
        )
        .outerjoin(Comment, Question.id == Comment.entry_id)
        .order_by(Comment.id)
        .outerjoin(
            CommentVote,
            and_(Comment.id == CommentVote.entry_id, Comment.user_id == user_id),
        )
        .outerjoin(AnswerComment, Answer.id == AnswerComment.entry_id)
        .order_by(AnswerComment.id)
        .outerjoin(
            AnswerCommentVote,
            and_(
                AnswerComment.id == AnswerCommentVote.entry_id,
                AnswerCommentVote.user_id == user_id,
            ),
        )
        .outerjoin(CommentUser, Comment.user_id == CommentUser.id)
        .outerjoin(AnswerCommentUser, AnswerComment.user_id == AnswerCommentUser.id)
        .options(
            contains_eager(Question.user),
            contains_eager(Question.votes.of_type(QuestionVote)),
            contains_eager(Question.comments).contains_eager(
                Comment.user.of_type(CommentUser)
            ),
            contains_eager(Question.comments).contains_eager(
                Comment.votes.of_type(CommentVote)
            ),
            contains_eager(Question.answers)
            .contains_eager(Answer.comments.of_type(AnswerComment))
            .contains_eager(AnswerComment.user.of_type(AnswerCommentUser)),
            contains_eager(Question.answers)
            .contains_eager(Answer.comments.of_type(AnswerComment))
            .contains_eager(AnswerComment.votes.of_type(AnswerCommentVote)),
            contains_eager(Question.answers).contains_eager(
                Answer.user.of_type(AnswerUser)
            ),
            contains_eager(Question.answers).contains_eager(
                Answer.votes.of_type(AnswerVote)
            ),
        )
        .filter(Question.id == id)
        .one()
    )


def get_list(db: Session, *, limit: int = 20, offset: int = 0) -> list[Question]:
    return (
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
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
        .order_by(Question.score.desc(), Question.answer_count.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def create(
    db: Session, *, user: User, title: str, content: str, tags: list[Tag]
) -> Question:
    question = Question(
        user=user,
        title=title,
        content=content,
        tags=tags,
    )

    db.add(question)
    db.commit()

    return question


def count(db: Session):
    return db.query(func.count(Question.id)).scalar()
