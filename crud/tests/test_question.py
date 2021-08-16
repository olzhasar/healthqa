import pytest
from faker import Faker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

import crud
from models import Comment, Question, Vote
from tests import factories

fake = Faker()


def test_get(db: Session, question, max_num_queries):
    with max_num_queries(1):
        from_db = crud.question.get(db, id=question.id)

    assert from_db
    assert isinstance(from_db, Question)
    assert from_db == question

    with pytest.raises(NoResultFound):
        crud.question.get(db, id=999)


def test_create(db: Session, user, tag, other_tag):
    title = fake.sentence()
    content = fake.paragraph()

    question = crud.question.create(
        db,
        user=user,
        title=title,
        content=content,
        tags=[tag.id, other_tag.id],
    )

    from_db = db.query(Question).filter(Question.id == question.id).one()

    assert question == from_db

    assert from_db.user == user
    assert from_db.title == title
    assert from_db.content == content
    assert set(from_db.tags) == set([tag, other_tag])


def test_update(db: Session, question, tag):
    tags = factories.TagFactory.create_batch(3)

    crud.question.update(
        db,
        question=question,
        new_title="New title",
        new_content="New content",
        tags=[tag.id for tag in tags],
    )

    from_db = db.query(Question).filter(Question.id == question.id).first()

    assert from_db.title == "New title"
    assert from_db.content == "New content"
    assert from_db.tags == tags


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


@pytest.fixture
def other_data():
    for answer in factories.AnswerFactory.create_batch(2):
        factories.VoteFactory(entry_id=answer.question.id)
        factories.VoteFactory(entry_id=answer.id)

        for comment in factories.CommentFactory.create_batch(
            2, entry_id=answer.question.id
        ):
            factories.VoteFactory(entry_id=comment.id)

        for comment in factories.CommentFactory.create_batch(2, entry_id=answer.id):
            factories.VoteFactory(entry_id=comment.id)


def test_get_with_related_single_query(
    db: Session, question_with_related, other_data, user, max_num_queries
):
    with max_num_queries(1):
        question = crud.question.get_with_related(
            db, id=question_with_related.id, user_id=user.id
        )

        assert question == question_with_related

        assert question.user.id
        assert question.user_vote.id

        for comment in question.comments:
            comment.id
            assert comment.user_vote.id


def test_get_with_related_correct_data(
    db: Session, question_with_related, other_data, user
):
    question = crud.question.get_with_related(
        db, id=question_with_related.id, user_id=user.id
    )

    assert (
        db.query(Vote.user_id)
        .filter(Vote.id == question.user_vote.id, Vote.entry_id == question.id)
        .scalar()
        == user.id
    )

    for comment in question.comments:
        assert (
            db.query(Comment.entry_id).filter(Comment.id == comment.id).scalar()
            == question.id
        )
        assert (
            db.query(Vote.user_id)
            .filter(Vote.id == comment.user_vote.id, Vote.entry_id == comment.id)
            .scalar()
            == user.id
        )


def test_get_with_related_no_user(db: Session, question_with_related, other_data):
    question = crud.question.get_with_related(db, id=question_with_related.id)

    assert not question.user_vote

    for comment in question.comments:
        assert not comment.user_vote


def test_count(db: Session):
    assert crud.question.count(db) == 0

    factories.QuestionFactory.create_batch(3)
    assert crud.question.count(db) == 3

    factories.QuestionFactory.create_batch(2)
    assert crud.question.count(db) == 5


class TestSearch:
    @pytest.fixture(autouse=True)
    def question_1(self):
        return factories.QuestionFactory(
            title="Upper back", content="Upper back pain after workout. Spine"
        )

    @pytest.fixture(autouse=True)
    def question_2(self):
        return factories.QuestionFactory(
            title="Spine", content="Lower back hurts sitting"
        )

    @pytest.fixture(autouse=True)
    def question_3(self):
        return factories.QuestionFactory(title="Sciatica", content="Sciatica hurts back")

    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            ("back", {"Upper back", "Spine", "Sciatica"}),
            ("spine", {"Upper back", "Spine"}),
            ("upper", {"Upper back"}),
            ("sitting", {"Spine"}),
            ("hurts", {"Spine", "Sciatica"}),
        ],
    )
    def test_ok(self, db: Session, query, expected):
        results = crud.question.search(db, query=query)

        assert {r.title for r in results} == expected
        assert crud.question.search_count(db, query=query) == len(expected)


def test_get_list_for_user(db: Session, user, other_user):
    questions = factories.QuestionFactory.create_batch(3, user=user)

    assert set(crud.question.get_list_for_user(db, user_id=user.id)) == set(questions)
    assert crud.question.get_list_for_user(db, user_id=other_user.id) == []
