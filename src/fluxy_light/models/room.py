from datetime import datetime, timezone
from uuid import UUID, uuid4

from fluxy_light.exceptions.validation import InvalidRoomError


class Room:
    def __init__(
        self,
        name: str,
        creator_id: UUID,
        is_moderated: bool,
    ) -> None:
        self.name, self.creator_id, self.is_moderated = self.validate_attributes(
            name, creator_id, is_moderated
        )
        self.id = uuid4()
        self.created_at = datetime.now(timezone.utc)

    @staticmethod
    def validate_attributes(
        name: str,
        creator_id: UUID,
        is_moderated: bool,
    ) -> tuple[str, UUID, bool]:
        if not isinstance(name, str):
            raise InvalidRoomError("Название комнаты должно быть строкой")

        if not isinstance(creator_id, UUID):
            raise InvalidRoomError("creator_id должен быть объектом UUID")

        if not isinstance(is_moderated, bool):
            raise InvalidRoomError("is_moderated должен быть типа bool")

        return name, creator_id, is_moderated

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
