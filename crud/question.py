from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.orm.session import Session

from models import Answer, Comment, Question, Tag, User


def get_by_id(db: Session, id: int) -> Question:
    return db.query(Question).filter(Question.id == id).one()


def get_for_view(db: Session, id: int, user_id: int = 0) -> Question:
    AnswerComment = aliased(Comment)
    AnswerUser = aliased(User)
    CommentUser = aliased(User)
    AnswerCommentUser = aliased(User)

    return (
        db.query(Question)
        .join(User, Question.user_id == User.id)
        .outerjoin(Answer, Question.id == Answer.question_id)
        .join(AnswerUser, Answer.user_id == AnswerUser.id)
        .outerjoin(Comment, Question.id == Comment.entry_id)
        .outerjoin(AnswerComment, Answer.id == AnswerComment.entry_id)
        .join(CommentUser, Comment.user_id == CommentUser.id)
        .join(AnswerCommentUser, AnswerComment.user_id == AnswerCommentUser.id)
        .options(
            contains_eager(Question.user),
            contains_eager(Question.comments).contains_eager(
                Comment.user.of_type(CommentUser)
            ),
            contains_eager(Question.answers)
            .contains_eager(Answer.comments.of_type(AnswerComment))
            .contains_eager(AnswerComment.user.of_type(AnswerCommentUser)),
        )
        .options(
            contains_eager(Question.answers).contains_eager(Answer.user, AnswerUser)
        )
        .filter(Question.id == id)
        .one()
    )


def get_all(db: Session, *, limit: int = 10):
    return (
        db.query(Question)
        .options(
            joinedload(Question.user),
            joinedload(Question.tags),
        )
        .order_by(Question.id.desc())
        .limit(limit)
        .all()
    )


def create(db: Session, *, user: User, title: str, content: str, tags: list[Tag]):
    question = Question(
        user=user,
        title=title,
        content=content,
        tags=tags,
    )

    db.add(question)
    db.commit()

    return question
