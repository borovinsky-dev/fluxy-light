from uuid import UUID, uuid4
from datetime import datetime, timezone
from re import fullmatch

from fluxy_light.models.role import Role


class User:
    """Класс для создания пользователей - базовый."""

    _count_default_user = 0

    def __init__(self, username: str | None = None, role: Role = Role.MEMBER) -> None:
        if username == None:
            username = self.set_default_user()
            name_after_validate = self.validate_username(username)
            username = name_after_validate
        else:
            self.validate_username(username)
        self.username = username
        self.role = role
        self.id: UUID = uuid4()
        self.created_at: datetime = datetime.now(timezone.utc)

    @classmethod
    def set_default_user(cls: User) -> str:
        cls._count_default_user += 1
        name: str = f"user_{cls._count_default_user}"
        return name

    @classmethod
    def get_counter(cls: User) -> int:
        return cls._count_default_user

    @staticmethod
    def validate_username(name: str):
        pattern = r"[A-Za-z0-9!#$%&()*+,\-./;<=>?@\[\]\\^_`{|}~]+"
        if type(name) != str:
            raise TypeError(f"Тип объекта должен быть {str.__name__}")
        if not 3 <= len(name) <= 15:
            raise ValueError("Username должен быть от 3 до 15 символов")
        if " " in name or ":" in name or "'" in name or '"' in name:
            raise ValueError("Username содержит запрещенные символы")
        if name.isdigit():
            raise ValueError("Username не может состоять только из цифр")
        if not fullmatch(pattern, name):
            raise ValueError("Username содержит недопустимые символы")
        return name

    @classmethod
    def from_db(
        cls,
        user_id: UUID,
        username: str,
        role: Role,
        created_at: datetime,
    ) -> User:
        object_user = cls(username=username, role=role)
        object_user.id = user_id
        object_user.created_at = created_at
        return object_user

    def __str__(self) -> str:
        return f"Объект класса {self.__class__.__name__}: ({self.id}, {self.username}, {self.created_at})"

    def __repr__(self) -> str:
        return f"Объект класса {self.__class__.__name__}: ({self.id!r}, {self.username!r}, {self.created_at!r})"


def main() -> None:
    user_1 = User()
    user_2 = User()
    user_3 = User("dima")

    print(user_1)
    print(user_2)
    print(user_3)

    print(repr(user_1))
    print(repr(user_3))


if __name__ == "__main__":
    print(f"Прямой запуск модуля {__name__}")
    main()
