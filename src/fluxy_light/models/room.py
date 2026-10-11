from uuid import UUID, uuid4
from datetime import datetime, timezone


class Room:
    def __init__(self, name: str, creator_id: UUID, is_moderated: bool):
        self.id = uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.name, self.creator_id, self.is_moderated = self.validate_attributes(
            name, creator_id, is_moderated
        )

    @staticmethod
    def validate_attributes(
        name: str, creator_id: UUID, is_moderated: bool
    ) -> tuple[str, UUID, bool]:
        if type(name) != str or type(creator_id) != UUID or type(is_moderated) != bool:
            raise TypeError("Неверные типы данных")
        return (name, creator_id, is_moderated)
