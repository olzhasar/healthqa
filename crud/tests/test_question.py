import random

import pytest
from faker import Faker
from sqlalchemy import func
from sqlalchemy.orm.session import Session

import crud
from models import Question
from models.answer import Answer
from tests import factories

fake = Faker()


def test_create_question(db: Session, user, tag, other_tag):
    title = fake.sentence()
    content = fake.paragraph()

    question = crud.question.create(
        db,
        user=user,
        title=title,
        content=content,
        tags=[tag, other_tag],
    )

    assert isinstance(question, Question)
    assert question.id
    assert question.user == user
    assert question.title == title
    assert question.content == content
    assert question.tags == [tag, other_tag]

    assert db.query(Question).filter(Question.user_id == user.id).first() == question


@pytest.fixture
def question_list():
    questions = factories.QuestionFactory.create_batch(5)

    for question in questions:
        factories.AnswerFactory.create_batch(random.randint(1, 3), question=question)


def test_get_list(db: Session, question_list):
    questions = crud.question.get_list(db)

    assert len(questions) == 5

    for question in questions:
        assert (
            question.answer_count
            == db.query(func.count(Answer.id))
            .filter(Answer.question_id == question.id)
            .scalar()
        )
