from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Any


class Conversation:
    """Класс отвечает за сущность создания отдельной переписки"""

    def __init__(self, ids: tuple[UUID, UUID]) -> None:
        # уникальный id переписки
        self.id = uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.ids = self.validate_ids(ids)

    def __str__(self) -> str:
        return f"Объект класса {self.__class__.__name__}: ({self.id}, {self.created_at}, {self.ids})"

    def __repr__(self) -> str:
        return f"Объект класса {self.__class__.__name__}: ({self.id!r}, {self.created_at!r}, {self.ids!r})"

    def __getattribute__(self, name) -> Any:
        if name == "attributes":
            return object.__getattribute__(self, "__dict__")
        return object.__getattribute__(self, name)

    # валидация атрибута ids
    @staticmethod
    def validate_ids(ids: tuple[UUID, UUID]) -> tuple[UUID, UUID]:
        if not isinstance(ids, tuple):
            raise TypeError("Аргумент должен быть кортежем (tuple)")
        if len(ids) != 2:
            raise ValueError("Кортеж должен содержать только 2 элемента")
        if any(not isinstance(element, UUID) for element in ids):
            raise TypeError("Все элементы кортежа должны быть объектами UUID")

        if ids[0] == ids[1]:
            raise ValueError("Участники переписки должны быть разными")
        return ids


def main() -> None:
    id_1 = uuid4()
    id_2 = uuid4()
    ids = (id_1, id_2)
    print(Conversation(ids))


if __name__ == "__main__":
    print(f"Прямой запус модуля {__name__}")
    main()
