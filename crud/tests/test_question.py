import pytest
from faker import Faker
from sqlalchemy.orm.session import Session

import crud
from models import Question
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
def question_list_params():
    return [
        ("first", 3, 2),
        ("second", 2, 5),
        ("third", 5, 5),
        ("fourth", 5, 3),
    ]


@pytest.fixture
def question_list(question_list_params):
    questions = []

    for title, answer_count, score in question_list_params:
        question = factories.QuestionFactory(title=title, score=score)
        factories.AnswerFactory.create_batch(answer_count, question=question)
        questions.append(question)

    return questions


class TestGetList:
    def test_ok(self, db: Session, question_list, question_list_params):
        questions = crud.question.get_list(db)

        assert len(questions) == 4

        question_list_params.reverse()

        for i, question in enumerate(questions):
            assert question.answer_count == question_list_params[i][1]

    @pytest.mark.parametrize(
        ("limit", "offset", "order"),
        [
            (2, 0, ["fourth", "third"]),
            (2, 2, ["second", "first"]),
        ],
    )
    def test_limit_offset(self, db: Session, question_list, limit, offset, order):
        questions = crud.question.get_list(db, limit=limit, offset=offset)

        assert [q.title for q in questions] == order


def test_get_popular_list(db: Session, question_list, question_list_params):
    questions = crud.question.get_popular_list(db)

    order = ["third", "second", "fourth", "first"]

    assert [q.title for q in questions] == order
