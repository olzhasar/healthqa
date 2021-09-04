import pytest

import repository as repo
from repository import exceptions
from storage import Store
from tests import factories

pytestmark = [pytest.mark.allow_db]


def test_get(store: Store, user, entry, max_num_queries):
    vote = factories.VoteFactory(entry_id=entry.id, user=user)

    with max_num_queries(1):
        assert repo.vote.get(store, user_id=user.id, entry_id=entry.id) == vote

    with max_num_queries(1):
        assert repo.vote.exists(store, user_id=user.id, entry_id=entry.id) is True


def test_get_non_existing(store: Store):
    with pytest.raises(exceptions.NotFoundError):
        repo.vote.get(store, user_id=999, entry_id=999)

    assert repo.vote.exists(store, user_id=999, entry_id=999) is False


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_new(store: Store, entry, user, input_val, value):
    vote = repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=input_val)

    from_db = repo.vote.get(store, user_id=user.id, entry_id=entry.id)

    assert from_db == vote
    assert from_db.value == value


@pytest.mark.parametrize("input_val", [-1, 3, 4, 99])
def test_register_invalid_value(store: Store, entry, user, input_val):
    with pytest.raises(ValueError) as exc:
        repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=input_val)
        assert str(exc) == "Invalid vote value"

    assert not repo.vote.exists(store, user_id=user.id, entry_id=entry.id)


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_same_value(store: Store, entry, user, input_val, value):
    factories.VoteFactory(entry_id=entry.id, user=user, value=value)

    with pytest.raises(ValueError) as exc:
        repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=input_val)
        assert str(exc) == "Vote already exists"


@pytest.mark.parametrize(
    ("input_val", "value"),
    [
        (1, 1),
        (2, -1),
    ],
)
def test_register_different_value(store: Store, entry, user, input_val, value):
    vote = factories.VoteFactory(entry_id=entry.id, user=user, value=-value)

    repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=input_val)

    store.db.refresh(vote)
    assert vote.value == value


def test_register_delete(store: Store, entry, user):
    factories.VoteFactory(entry_id=entry.id, user=user, value=1)

    repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=0)

    assert not repo.vote.exists(store, user_id=user.id, entry_id=entry.id)


def test_register_delete_not_existing(store: Store, entry, user):
    with pytest.raises(ValueError) as exc:
        repo.vote.record(store, user_id=user.id, entry_id=entry.id, value=0)
        assert str(exc) == "Vote does not exist"


def test_score_calculation(store: Store, entry, question, user):
    another_entry = factories.QuestionFactory(user=user)

    factories.VoteFactory.create_batch(5, entry_id=entry.id, value=1)

    store.db.refresh(entry)
    store.db.refresh(user)

    assert entry.score == user.score == 5

    factories.VoteFactory.create_batch(3, entry_id=another_entry.id, value=1)

    store.db.refresh(entry)
    store.db.refresh(another_entry)
    store.db.refresh(user)

    assert entry.score == 5
    assert another_entry.score == 3
    assert user.score == 8
