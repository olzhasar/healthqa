from unittest.mock import MagicMock

import pytest
from faker import Faker
from slugify import slugify

import repository as repo
from models import Comment, Vote
from storage import Store
from tests import factories

fake = Faker()

pytestmark = [pytest.mark.allow_db, pytest.mark.allow_redis]


def test_get(store: Store, question, max_num_queries):
    with max_num_queries(1):
        assert repo.question.get(store, question.id) == question


def test_first_for_user(store: Store, question, other_user):
    assert repo.question.first_for_user(store, question.user) == question
    assert repo.question.first_for_user(store, other_user) is None


@pytest.mark.allow_redis
def test_get_view_count(store: Store):
    assert repo.question.get_view_count(store, 1) == 0

    key = repo.question.REDIS_QUESTION_VIEW_KEY.format(id=1)

    store.redis.pfadd(key, "192.168.1.1")
    assert repo.question.get_view_count(store, 1) == 1

    store.redis.pfadd(key, "192.168.1.1")
    assert repo.question.get_view_count(store, 1) == 1

    store.redis.pfadd(key, "192.168.1.2")
    assert repo.question.get_view_count(store, 1) == 2


@pytest.mark.allow_redis
def test_register_view(store: Store):
    assert repo.question.get_view_count(store, 1) == 0

    repo.question.register_view(store, 1, "192.168.1.1")
    assert repo.question.get_view_count(store, 1) == 1

    repo.question.register_view(store, 1, "192.168.1.2")
    assert repo.question.get_view_count(store, 1) == 2


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


@pytest.mark.allow_redis
def test_get_with_related_single_query(
    store: Store,
    question_with_related,
    other_data,
    user,
    max_num_queries,
):
    with max_num_queries(1):
        question = repo.question.get_with_related(
            store, question_with_related.id, user_id=user.id
        )

        assert question == question_with_related

        assert question.user.id
        assert question.user_vote.id
        assert question.view_count == 0

        for comment in question.comments:
            comment.id
            assert comment.user_vote.id


def test_get_with_related_view_count(store: Store, question, user):
    question = repo.question.get_with_related(store, question.id, user_id=user.id)
    assert question.view_count == 0

    repo.question.register_view(store, question.id, "192.168.1.1")
    question = repo.question.get_with_related(store, question.id, user_id=user.id)
    assert question.view_count == 1


def test_get_with_related_correct_data(
    store: Store,
    question_with_related,
    other_data,
    user,
):
    question = repo.question.get_with_related(
        store, question_with_related.id, user_id=user.id
    )

    assert (
        store.db.query(Vote.user_id)
        .filter(Vote.id == question.user_vote.id, Vote.entry_id == question.id)
        .scalar()
        == user.id
    )

    for comment in question.comments:
        assert (
            store.db.query(Comment.entry_id).filter(Comment.id == comment.id).scalar()
            == question.id
        )
        assert (
            store.db.query(Vote.user_id)
            .filter(Vote.id == comment.user_vote.id, Vote.entry_id == comment.id)
            .scalar()
            == user.id
        )


def test_get_with_related_no_user(store: Store, question_with_related, other_data):
    question = repo.question.get_with_related(store, question_with_related.id)

    assert not question.user_vote

    for comment in question.comments:
        assert not comment.user_vote


def test_create(store: Store, user, tag, other_tag):
    title = fake.sentence()
    content = fake.paragraph()

    question = repo.question.create(
        store,
        user=user,
        title=title,
        content=content,
        tags=[tag.id, other_tag.id],
    )

    from_db = repo.question.get(store, question.id)

    assert question == from_db

    assert from_db.user == user
    assert from_db.title == title
    assert from_db.content == content
    assert from_db.slug == slugify(from_db.title)
    assert set(from_db.tags) == set([tag, other_tag])


def test_update(store: Store, question, tag):
    tags = factories.TagFactory.create_batch(3)

    repo.question.update(
        store,
        question,
        new_title="New title",
        new_content="New content",
        tags=[tag.id for tag in tags],
    )

    store.refresh(question)

    assert question.title == "New title"
    assert question.slug == slugify(question.title)
    assert question.content == "New content"
    assert question.tags == tags


@pytest.fixture
def questions():
    return factories.QuestionFactory.create_batch(4)


def test_all_view_counts(store: Store, questions):
    view_counts = [2, 3, 4, 1]

    for i, question in enumerate(questions):
        for j in range(view_counts[i]):
            repo.question.register_view(store, question.id, f"192.168.1.{j}")

    result = repo.question.all(store)
    for question in result:
        assert question.view_count == repo.question.get_view_count(store, question.id)

    assert [q.view_count for q in result] == list(reversed(view_counts))


@pytest.mark.parametrize(
    ("page", "per_page", "exp_n_pages", "exp_slice"),
    [
        (1, 4, 1, (0, 4)),
        (1, 2, 2, (0, 2)),
        (2, 2, 2, (2, 4)),
        (1, 3, 2, (0, 3)),
    ],
)
def test_list(
    store: Store, questions, max_num_queries, page, per_page, exp_n_pages, exp_slice
):
    with max_num_queries(2):
        paginator = repo.question.list(store, page=page, per_page=per_page)

    reversed_questions = questions[::-1]
    assert paginator.objects == reversed_questions[slice(*exp_slice)]
    assert paginator.total == len(questions)
    assert paginator.page == page
    assert paginator.per_page == per_page
    assert len(paginator) == exp_n_pages


@pytest.fixture
def question_list_params():
    return [
        ("first", 3, 2, "tag_1"),
        ("second", 2, 5, "tag_2"),
        ("third", 5, 5, "tag_2"),
        ("fourth", 5, 3, "tag_1"),
    ]


@pytest.fixture
def question_list(question_list_params):
    questions = []

    for title, answer_count, score, tag_name in question_list_params:
        tag = factories.TagFactory(name=tag_name)
        question = factories.QuestionFactory(title=title, score=score, tags=[tag])
        factories.AnswerFactory.create_batch(answer_count, question=question)
        questions.append(question)

    return questions


@pytest.mark.parametrize(
    ("tag_name", "result"),
    [
        ("tag_1", ["first", "fourth"]),
        ("tag_2", ["second", "third"]),
    ],
)
def test_list_by_tag(store: Store, question_list, tag_name, result, max_num_queries):
    tag = factories.TagFactory(name=tag_name)

    with max_num_queries(2):
        paginator = repo.question.list_by_tag(store, tag=tag)

    assert {q.title for q in paginator.objects} == set(result)


@pytest.fixture()
def user_questions(user):
    return factories.QuestionFactory.create_batch(4, user=user)


def test_all_for_user(store: Store, user, other_user, user_questions):
    assert set(repo.question.all_for_user(store, user)) == set(user_questions)
    assert repo.question.all_for_user(store, other_user) == []


@pytest.mark.parametrize(
    ("page", "per_page", "exp_n_pages", "exp_slice"),
    [
        (1, 4, 1, (0, 4)),
        (1, 2, 2, (0, 2)),
        (2, 2, 2, (2, 4)),
        (1, 3, 2, (0, 3)),
    ],
)
def test_list_for_user(
    store: Store,
    questions,
    user_questions,
    user,
    max_num_queries,
    page,
    per_page,
    exp_n_pages,
    exp_slice,
):
    with max_num_queries(2):
        paginator = repo.question.list_for_user(
            store, user, page=page, per_page=per_page
        )

    reversed_questions = user_questions[::-1]
    assert paginator.objects == reversed_questions[slice(*exp_slice)]
    assert paginator.total == len(questions)
    assert paginator.page == page
    assert paginator.per_page == per_page
    assert len(paginator) == exp_n_pages


@pytest.fixture
def questions_for_search():
    return [
        factories.QuestionFactory(
            title="Upper back", content="Upper back pain after workout. Spine"
        ),
        factories.QuestionFactory(title="Spine", content="Lower back hurts sitting"),
        factories.QuestionFactory(title="Sciatica", content="Sciatica hurts back"),
    ]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("back", {"Upper back", "Spine", "Sciatica"}),
        ("spine", {"Upper back", "Spine"}),
        ("upper", {"Upper back"}),
        ("upper back", {"Upper back"}),
        ("hurts", {"Spine", "Sciatica"}),
        ("sitting", {"Spine"}),
        ("sitting\\", {"Spine"}),
    ],
)
def test_search(store: Store, questions_for_search, query, expected):
    paginator = repo.question.search(store, query)

    assert {r.title for r in paginator.objects} == expected
    assert paginator.total == len(expected)


def test_update_search_indexes(
    store: Store, with_app_context, meili_client_mock: MagicMock
):
    questions = factories.QuestionFactory.create_batch(2)

    docs = []
    for question in questions:
        docs.append(
            {
                "id": str(question.id),
                "title": question.title,
                "content": question.content,
                "url": question.url,
            }
        )

    repo.question.update_search_indexes(store, *questions)

    meili_client_mock.index("questions").add_documents.assert_called_once_with(docs)
