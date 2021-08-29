import pytest
from faker import Faker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

import crud
from models import Answer, Comment, Vote
from tests import factories

fake = Faker()


def test_get(db: Session, answer, max_num_queries):
    with max_num_queries(1):
        from_db = crud.answer.get(db, id=answer.id)

    assert from_db
    assert isinstance(from_db, Answer)

    with pytest.raises(NoResultFound):
        crud.user.get(db, id=999)


@pytest.mark.parametrize("answer__content", ["Old content"])
def test_update(db: Session, answer):
    crud.answer.update(db, answer=answer, new_content="New content")

    db.refresh(answer)
    assert answer.content == "New content"


def test_create_answer(db: Session, user, question):
    content = fake.paragraph()

    answer = crud.answer.create(
        db,
        user=user,
        question_id=question.id,
        content=content,
    )

    from_db = db.query(Answer).filter(Answer.user_id == user.id).one()

    assert from_db == answer
    assert from_db.id
    assert from_db.user == user
    assert from_db.question == question
    assert from_db.content == content


def test_get_list_for_user(db: Session, user, other_user):
    answers = factories.AnswerFactory.create_batch(3, user=user)
    factories.AnswerFactory.create_batch(3)

    assert set(crud.answer.get_list_for_user(db, user_id=user.id)) == set(answers)
    assert crud.answer.get_list_for_user(db, user_id=other_user.id) == []


def test_get_list_for_question(db: Session, question_with_related, user):
    answers = crud.answer.get_list_for_question(
        db, question_id=question_with_related.id, user_id=user.id
    )

    assert len(answers) == 2
    assert set(answers) == set(question_with_related.answers)


def test_get_list_for_question_single_query(
    db: Session, question_with_related, user, max_num_queries
):
    with max_num_queries(1):
        answers = crud.answer.get_list_for_question(
            db, question_id=question_with_related.id, user_id=user.id
        )

        for answer in answers:
            answer.id
            answer.user.id

            assert answer.user_vote
            for comment in answer.comments:
                comment.id
                assert comment.user_vote


def test_get_list_for_question_correct_data(db: Session, question_with_related, user):
    answers = crud.answer.get_list_for_question(
        db, question_id=question_with_related.id, user_id=user.id
    )

    for answer in answers:
        assert (
            answer.user.id
            == db.query(Answer.user_id).filter(Answer.id == answer.id).scalar()
        )

        assert (
            db.query(Vote.user_id)
            .filter(Vote.id == answer.user_vote.id, Vote.entry_id == answer.id)
            .scalar()
            == user.id
        )
        for comment in answer.comments:
            assert (
                db.query(Comment.entry_id).filter(Comment.id == comment.id).scalar()
                == answer.id
            )
            assert (
                db.query(Vote.user_id)
                .filter(Vote.id == comment.user_vote.id, Vote.entry_id == comment.id)
                .scalar()
                == user.id
            )


def test_get_list_for_question_no_user(db: Session, question_with_related, user):
    answers = crud.answer.get_list_for_question(db, question_id=question_with_related.id)

    for answer in answers:
        assert not answer.user_vote

        for comment in answer.comments:
            assert not comment.user_vote


def test_get_list_for_answer_sorting(db: Session, question):
    factories.AnswerFactory(question=question, content="first", score=5)
    factories.AnswerFactory(question=question, content="second", score=5)
    factories.AnswerFactory(question=question, content="third", score=0)
    factories.AnswerFactory(question=question, content="fourth", score=7)

    answers = crud.answer.get_list_for_question(db, question_id=question.id)

    assert [a.content for a in answers] == ["fourth", "second", "first", "third"]
