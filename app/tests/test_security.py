from app.security import check_password, hash_password


def test_hash_password():
    pass1 = "123qweasd"
    hash1 = hash_password(pass1)

    assert isinstance(hash1, str)
    assert hash1 != pass1
    assert check_password("123qweasd", hash1)

    pass2 = "another_password"
    hash2 = hash_password(pass2)

    assert check_password("another_password", hash2)
    assert hash2 != hash1
