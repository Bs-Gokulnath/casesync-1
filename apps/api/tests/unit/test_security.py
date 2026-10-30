from app.security.passwords import hash_password, verify_password
from app.security.sessions import csrf_tokens_match, generate_csrf_token, hash_token


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("Sup3r-Secret!")
    assert verify_password("Sup3r-Secret!", hashed)


def test_wrong_password_fails_verification() -> None:
    hashed = hash_password("Sup3r-Secret!")
    assert not verify_password("wrong-password", hashed)


def test_password_hash_is_not_the_plaintext() -> None:
    hashed = hash_password("Sup3r-Secret!")
    assert hashed != "Sup3r-Secret!"


def test_token_hash_is_deterministic_and_one_way() -> None:
    token = generate_csrf_token()
    assert hash_token(token) == hash_token(token)
    assert hash_token(token) != token


def test_csrf_tokens_match_requires_exact_value() -> None:
    expected = generate_csrf_token()
    assert csrf_tokens_match(expected, expected)
    assert not csrf_tokens_match("something-else", expected)
    assert not csrf_tokens_match(None, expected)
