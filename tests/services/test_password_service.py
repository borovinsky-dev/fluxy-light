import pytest

from fluxy_light.services.password_service import PasswordService


@pytest.fixture
def password_service() -> PasswordService:
    return PasswordService()


def test_hash_password_returns_salt_and_hash(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    assert isinstance(salt, bytes)
    assert isinstance(password_hash, bytes)


def test_hash_password_returns_correct_lengths(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    assert len(salt) == 16
    assert len(password_hash) == 64


def test_hash_password_generates_different_salts(
    password_service: PasswordService,
) -> None:
    salt_1, hash_1 = password_service.hash_password("MySecret123")
    salt_2, hash_2 = password_service.hash_password("MySecret123")

    assert salt_1 != salt_2
    assert hash_1 != hash_2


def test_verify_password_returns_true_for_correct_password(
    password_service: PasswordService,
) -> None:
    password = "MySecret123"
    salt, password_hash = password_service.hash_password(password)

    result = password_service.verify_password(
        password,
        salt,
        password_hash,
    )

    assert result is True


def test_verify_password_returns_false_for_wrong_password(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    result = password_service.verify_password(
        "WrongPassword",
        salt,
        password_hash,
    )

    assert result is False


def test_hash_password_rejects_empty_password(
    password_service: PasswordService,
) -> None:
    with pytest.raises(ValueError):
        password_service.hash_password("")


@pytest.mark.parametrize("password", [None, 123, [], {}, True])
def test_hash_password_rejects_non_string_password(
    password_service: PasswordService,
    password: object,
) -> None:
    with pytest.raises(TypeError):
        password_service.hash_password(password)


def test_verify_password_rejects_non_string_password(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    with pytest.raises(TypeError):
        password_service.verify_password(123, salt, password_hash)


def test_verify_password_rejects_invalid_salt_type(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    with pytest.raises(TypeError):
        password_service.verify_password("MySecret123", "invalid", password_hash)


def test_verify_password_rejects_invalid_hash_type(
    password_service: PasswordService,
) -> None:
    salt, password_hash = password_service.hash_password("MySecret123")

    with pytest.raises(TypeError):
        password_service.verify_password("MySecret123", salt, "invalid")
