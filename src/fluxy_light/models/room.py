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

    @classmethod
    def from_db(
        cls,
        id: str,
        name: str,
        creator_id: str,
        is_moderated: int,
        created_at: str,
    ) -> "Room":
        room_object = cls(
            name=name,
            creator_id=UUID(creator_id),
            is_moderated=bool(is_moderated),
        )
        room_object.id = UUID(id)
        room_object.created_at = datetime.fromisoformat(created_at)

        return room_object
