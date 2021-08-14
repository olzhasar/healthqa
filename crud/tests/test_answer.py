import pytest
from faker import Faker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

import crud
from models import Answer
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

    assert isinstance(answer, Answer)
    assert answer.id
    assert answer.user == user
    assert answer.question == question
    assert answer.content == content

    assert db.query(Answer).filter(Answer.user_id == user.id).first() == answer


def test_list_for_user(db: Session, user, other_user):
    answers = factories.AnswerFactory.create_batch(3, user=user)
    factories.AnswerFactory.create_batch(3)

    assert set(crud.answer.list_for_user(db, user_id=user.id)) == set(answers)
    assert crud.question.list_for_user(db, user_id=other_user.id) == []
