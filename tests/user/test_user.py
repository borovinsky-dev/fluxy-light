# автоматическое генерирование кода тестирования для класса user
from datetime import datetime
from uuid import UUID

import pytest

from src.models.user import User


class TestUser:
    """Тесты класса User."""

    # Сбрасываем счётчик перед каждым тестом,
    # а после теста возвращаем исходное значение.
    @pytest.fixture(autouse=True)
    def reset_counter(self):
        original_count = User._count_default_user
        User._count_default_user = 0

        yield

        User._count_default_user = original_count

    # ---------- Валидация username ----------

    @pytest.mark.parametrize(
        "username",
        [
            "dima",
            "Dima",
            "user123",
            "123user",
            "user_name",
            "user-name",
            "user.name",
            "abc!#$",
            "abc[]",
            "abc\\def",
            "abc^_`",
            "abc{|}~",
            "abc",  # минимальная длина: 3
            "a" * 15,  # максимальная длина: 15
        ],
    )
    def test_validate_username_accepts_valid_names(self, username):
        assert User.validate_username(username) == username

    @pytest.mark.parametrize(
        "username",
        [
            123,
            12.5,
            None,
            True,
            False,
            [],
            {},
            (),
            object(),
        ],
    )
    def test_validate_username_rejects_non_string(self, username):
        with pytest.raises(TypeError):
            User.validate_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "",
            "a",
            "ab",
            "a" * 16,
        ],
    )
    def test_validate_username_rejects_invalid_length(self, username):
        with pytest.raises(ValueError):
            User.validate_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "123",
            "123456",
            "000",
        ],
    )
    def test_validate_username_rejects_digits_only(self, username):
        with pytest.raises(ValueError):
            User.validate_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "ab c",
            "ab:c",
            "ab'c",
            'ab"c',
        ],
    )
    def test_validate_username_rejects_forbidden_characters(self, username):
        with pytest.raises(ValueError):
            User.validate_username(username)

    @pytest.mark.parametrize(
        "username",
        [
            "абв",  # кириллица
            "abв",  # смешанная латиница и кириллица
            "abé",  # не ASCII
            "ab🙂",  # emoji
            "ab\tc",  # табуляция
            "ab\nc",  # перевод строки
            "ab\rc",  # возврат каретки
        ],
    )
    def test_validate_username_rejects_non_ascii_characters(self, username):
        with pytest.raises(ValueError):
            User.validate_username(username)

    # ---------- Создание пользователя ----------

    def test_user_generates_default_username(self):
        user = User()

        assert user.name == "user_1"

    def test_user_generates_sequential_default_usernames(self):
        user_1 = User()
        user_2 = User()
        user_3 = User()

        assert user_1.name == "user_1"
        assert user_2.name == "user_2"
        assert user_3.name == "user_3"

    def test_user_accepts_custom_username(self):
        user = User("dima")

        assert user.name == "dima"

    def test_custom_username_does_not_increment_default_counter(self):
        User("dima")

        assert User.get_counter() == 0

    def test_invalid_username_prevents_user_creation(self):
        with pytest.raises(ValueError):
            User("123")

    # ---------- Счётчик ----------

    def test_set_default_user_increments_counter(self):
        assert User.get_counter() == 0

        User.set_default_user()

        assert User.get_counter() == 1

    def test_get_counter_returns_current_value(self):
        User()
        User()

        assert User.get_counter() == 2

    # ---------- Поля объекта ----------

    def test_user_generates_uuid(self):
        user = User("dima")

        assert isinstance(user.id, UUID)

    def test_user_generates_unique_ids(self):
        user_1 = User("dima")
        user_2 = User("alex")

        assert user_1.id != user_2.id

    def test_user_sets_creation_datetime(self):
        user = User("dima")

        assert isinstance(user.created_at, datetime)

    # ---------- Строковое представление ----------

    def test_str_contains_user_data(self):
        user = User("dima")

        result = str(user)

        assert "User" in result
        assert str(user.id) in result
        assert "dima" in result
        assert str(user.created_at) in result

    def test_repr_contains_user_data(self):
        user = User("dima")

        result = repr(user)

        assert "User" in result
        assert repr(user.id) in result
        assert repr(user.name) in result
        assert repr(user.created_at) in result
