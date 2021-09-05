import pytest
from faker import Faker

import repository as repo
from models import Answer, Comment, Vote
from repository import exceptions
from storage import Store
from tests import factories

fake = Faker()

pytestmark = [pytest.mark.allow_db]


def test_get(store: Store, answer, max_num_queries):
    with max_num_queries(1):
        assert repo.answer.get(store, answer.id) == answer


def test_get_non_existing(store: Store):
    with pytest.raises(exceptions.NotFoundError):
        repo.answer.get(store, 999)


@pytest.mark.parametrize("answer__content", ["Old content"])
def test_update(store: Store, answer):
    repo.answer.update(store, answer=answer, new_content="New content")

    store.db.refresh(answer)
    assert answer.content == "New content"


def test_create_answer(store: Store, user, question):
    content = fake.paragraph()

    answer = repo.answer.create(
        store,
        user=user,
        question_id=question.id,
        content=content,
    )

    from_db = repo.answer.get(store, answer.id)

    assert from_db == answer
    assert from_db.id
    assert from_db.user == user
    assert from_db.question == question
    assert from_db.content == content


def test_all_for_user(store: Store, user, other_user):
    answers = factories.AnswerFactory.create_batch(3, user=user)
    factories.AnswerFactory.create_batch(3)

    assert set(repo.answer.all_for_user(store, user)) == set(answers)
    assert repo.answer.all_for_user(store, other_user) == []


def test_all_for_question(store: Store, question_with_related, user):
    answers = repo.answer.all_for_question(
        store, question_id=question_with_related.id, user_id=user.id
    )

    assert len(answers) == 2
    assert set(answers) == set(question_with_related.answers)


def test_all_for_question_single_query(
    store: Store, question_with_related, user, max_num_queries
):
    with max_num_queries(1):
        answers = repo.answer.all_for_question(
            store, question_id=question_with_related.id, user_id=user.id
        )

        for answer in answers:
            answer.id
            answer.user.id

            assert answer.user_vote
            for comment in answer.comments:
                comment.id
                assert comment.user_vote


def test_all_for_question_correct_data(store: Store, question_with_related, user):
    answers = repo.answer.all_for_question(
        store, question_id=question_with_related.id, user_id=user.id
    )

    for answer in answers:
        assert (
            answer.user.id
            == store.db.query(Answer.user_id).filter(Answer.id == answer.id).scalar()
        )

        assert (
            store.db.query(Vote.user_id)
            .filter(Vote.id == answer.user_vote.id, Vote.entry_id == answer.id)
            .scalar()
            == user.id
        )
        for comment in answer.comments:
            assert (
                store.db.query(Comment.entry_id)
                .filter(Comment.id == comment.id)
                .scalar()
                == answer.id
            )
            assert (
                store.db.query(Vote.user_id)
                .filter(Vote.id == comment.user_vote.id, Vote.entry_id == comment.id)
                .scalar()
                == user.id
            )


def test_all_for_question_no_user(store: Store, question_with_related, user):
    answers = repo.answer.all_for_question(store, question_id=question_with_related.id)

    for answer in answers:
        assert not answer.user_vote

        for comment in answer.comments:
            assert not comment.user_vote


def test_all_for_question_sorting(store: Store, question):
    factories.AnswerFactory(question=question, content="first", score=5)
    factories.AnswerFactory(question=question, content="second", score=5)
    factories.AnswerFactory(question=question, content="third", score=0)
    factories.AnswerFactory(question=question, content="fourth", score=7)

    answers = repo.answer.all_for_question(store, question_id=question.id)

    assert [a.content for a in answers] == ["fourth", "second", "first", "third"]
