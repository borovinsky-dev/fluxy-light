from datetime import datetime, timezone
from uuid import UUID


from fluxy_light.exceptions.validation import InvalidRoomError


class RoomMember:
    def __init__(
        self,
        room_id: UUID,
        user_id: UUID,
        role: str = "member",
    ) -> None:
        self.room_id, self.user_id, self.role = self.validate_attributes(
            room_id, user_id, role
        )
        self.joined_at = datetime.now(timezone.utc)

    @staticmethod
    def validate_attributes(
        room_id: UUID,
        user_id: UUID,
        role: str,
    ) -> tuple[UUID, UUID, str]:
        if not isinstance(room_id, UUID):
            raise InvalidRoomError("room_id должен быть объектом UUID")

        if not isinstance(user_id, UUID):
            raise InvalidRoomError("user_id должен быть объектом UUID")

        if role not in ("owner", "moderator", "member"):
            raise InvalidRoomError("Недопустимая роль участника комнаты")

    @classmethod
    def from_db(
        cls,
        room_id: str,
        user_id: str,
        role: str,
        joined_at: str,
    ) -> RoomMember:
        member = cls(
            room_id=UUID(room_id),
            user_id=UUID(user_id),
            role=role,
        )
        member.joined_at = datetime.fromisoformat(joined_at)

        return member
