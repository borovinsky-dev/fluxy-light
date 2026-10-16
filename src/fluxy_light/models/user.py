from uuid import UUID, uuid4
from datetime import datetime, timezone
from re import fullmatch

from fluxy_light.models.role import Role
from fluxy_light.exceptions.validation import (
    InvalidEmailError,
    InvalidUsernameError,
)


class User:
    """Класс для создания пользователей — базовый."""

    _count_default_user = 0

    def __init__(
        self,
        email: str,
        username: str | None = None,
        role: Role = Role.MEMBER,
    ) -> None:
        if username is None:
            username = self.set_default_user()

        self.username = self.validate_username(username)
        self.email = self.validate_email(email)
        self.role = role
        self.id: UUID = uuid4()
        self.created_at: datetime = datetime.now(timezone.utc)

    @classmethod
    def set_default_user(cls) -> str:
        cls._count_default_user += 1
        return f"user_{cls._count_default_user}"

    @classmethod
    def get_counter(cls) -> int:
        return cls._count_default_user

    @staticmethod
    def validate_username(name: str) -> str:
        pattern = r"[A-Za-z0-9!#$%&()*+,\-./;<=>?@\[\]\\^_`{|}~]+"

        if not isinstance(name, str):
            raise InvalidUsernameError(f"Тип объекта должен быть {str.__name__}")

        if not 3 <= len(name) <= 15:
            raise InvalidUsernameError("Username должен быть от 3 до 15 символов")

        if " " in name or ":" in name or "'" in name or '"' in name:
            raise InvalidUsernameError("Username содержит запрещенные символы")

        if name.isdigit():
            raise InvalidUsernameError("Username не может состоять только из цифр")

        if not fullmatch(pattern, name):
            raise InvalidUsernameError("Username содержит недопустимые символы")

        return name

    @staticmethod
    def validate_email(email: str) -> str:
        if not isinstance(email, str):
            raise InvalidEmailError("Email должен быть строковым типом данных")

        if not email:
            raise InvalidEmailError("Email не может быть пустым")

        if email != email.strip():
            raise InvalidEmailError(
                "Email не должен содержать пробелы в начале и конце"
            )

        if any(char.isspace() for char in email):
            raise InvalidEmailError("Email не должен содержать пробельные символы")

        if email.count("@") != 1:
            raise InvalidEmailError("Email должен содержать ровно один символ @")

        local, domain = email.split("@")

        if not local or not domain:
            raise InvalidEmailError("Локальная часть и домен не должны быть пустыми")

        if (
            local.startswith(".")
            or local.endswith(".")
            or ".." in local
            or ".." in domain
        ):
            raise InvalidEmailError("Некорректное расположение точек в email")

        if "." not in domain:
            raise InvalidEmailError("Домен должен содержать точку")

        pattern = (
            r"[A-Za-z0-9_%\-]+"
            r"@"
            r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
            r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*"
            r"\.[A-Za-z]{2,}"
        )

        if not fullmatch(pattern, email):
            raise InvalidEmailError("Email не соответствует допустимому формату")

        return email

    @classmethod
    def from_db(
        cls,
        user_id: UUID,
        username: str,
        email: str,
        role: Role,
        created_at: datetime,
    ) -> "User":
        object_user = cls(
            email=email,
            username=username,
            role=role,
        )
        object_user.id = user_id
        object_user.created_at = created_at
        return object_user

    def __str__(self) -> str:
        return (
            f"Объект класса {self.__class__.__name__}: "
            f"({self.id}, {self.username}, {self.created_at})"
        )

    def __repr__(self) -> str:
        return (
            f"Объект класса {self.__class__.__name__}: "
            f"({self.id!r}, {self.username!r}, {self.created_at!r})"
        )
