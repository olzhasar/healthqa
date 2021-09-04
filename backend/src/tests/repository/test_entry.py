from datetime import datetime

import pytest

import repository as repo
from repository import exceptions
from storage import Store
from tests import factories

pytestmark = [pytest.mark.allow_db]


def test_get(store: Store, entry, max_num_queries):
    with max_num_queries(1):
        assert repo.entry.get(store, entry.id) == entry


def test_get_non_existing(store: Store, max_num_queries):
    with pytest.raises(exceptions.NotFoundError):
        assert repo.entry.get(store, 999)


def test_exists(store: Store, entry, max_num_queries):
    assert repo.entry.exists(store, entry.id) is True


def test_exists_non_existing(store: Store, max_num_queries):
    assert repo.entry.exists(store, 999) is False


def test_get_with_user_vote(store: Store, entry, user, max_num_queries):
    factories.VoteFactory.create_batch(2, entry_id=entry.id)
    user_vote = factories.VoteFactory(entry_id=entry.id, user=user)

    with max_num_queries(1):
        from_db = repo.entry.get_with_user_vote(store, id=entry.id, user_id=user.id)

        assert from_db == entry
        assert from_db.user_vote == user_vote


def test_get_with_user_votes_no_vote(store: Store, entry, user, max_num_queries):
    factories.VoteFactory.create_batch(2, entry_id=entry.id)

    from_db = repo.entry.get_with_user_vote(store, id=entry.id, user_id=user.id)

    assert from_db == entry
    assert not from_db.user_vote


@pytest.mark.freeze_time("2030-01-01")
def test_mark_as_deleted(store: Store, entry, user):
    assert not entry.deleted_at

    repo.entry.mark_as_deleted(store, id=entry.id, user_id=user.id)

    store.db.refresh(entry)
    assert entry.deleted_at == datetime(2030, 1, 1)


def test_mark_as_deleted_not_found(store: Store, user):
    with pytest.raises(exceptions.NotFoundError):
        repo.entry.mark_as_deleted(store, id=999, user_id=user.id)


def test_mark_as_deleted_wrong_user(store: Store, entry, other_user):
    with pytest.raises(exceptions.NotFoundError):
        repo.entry.mark_as_deleted(store, id=entry.id, user_id=other_user.id)
