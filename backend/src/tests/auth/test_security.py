import secrets

import pytest
from freezegun import freeze_time

from auth import security


def test_hash_password():
    pass1 = "123qweasd"
    hash1 = security.hash_password(pass1)

    assert isinstance(hash1, str)
    assert hash1 != pass1
    assert security.check_password("123qweasd", hash1)

    pass2 = "another_password"
    hash2 = security.hash_password(pass2)

    assert security.check_password("another_password", hash2)
    assert hash2 != hash1


def test_make_url_safe_token():
    token_1 = security.make_url_safe_token(user_id=5)
    assert isinstance(token_1, str)

    token_2 = security.make_url_safe_token(user_id=10)
    assert isinstance(token_2, str)

    assert token_1 != token_2


@pytest.mark.parametrize("user_id", [1, 5, 999])
def test_get_user_id_from_token(user_id):
    token = security.make_url_safe_token(user_id)

    assert security.get_user_id_from_token(token, max_age=100) == user_id


def test_get_user_id_from_token_invalid_token():
    token = secrets.token_urlsafe()

    with pytest.raises(ValueError) as e:
        security.get_user_id_from_token(token, max_age=100)
        assert str(e) == "Invalid token"


def test_get_user_id_from_token_expiration():
    with freeze_time("2020-01-01 12:00:00") as frozen:
        token = security.make_url_safe_token(99)

        frozen.move_to("2020-01-01 12:02:00")

        assert security.get_user_id_from_token(token, max_age=150) == 99

        with pytest.raises(ValueError):
            security.get_user_id_from_token(token, max_age=100)
