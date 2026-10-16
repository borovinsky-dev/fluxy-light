from datetime import datetime, timezone
from uuid import UUID, uuid4

from fluxy_light.exceptions.validation import InvalidMessageError


class Message:
    """Класс для создания сообщений."""

    def __init__(
        self,
        sender_id: UUID,
        text: str,
        conversation_id: UUID | None = None,
        room_id: UUID | None = None,
    ) -> None:
        (
            self.sender_id,
            self.conversation_id,
            self.room_id,
            self.text,
        ) = self.validate_attributes(
            sender_id,
            conversation_id,
            room_id,
            text,
        )

        self.id: UUID = uuid4()
        self.created_at: datetime = datetime.now(timezone.utc)

    @staticmethod
    def validate_attributes(
        sender_id: UUID,
        conversation_id: UUID | None,
        room_id: UUID | None,
        text: str,
    ) -> tuple[UUID, UUID | None, UUID | None, str]:
        """Проверяет атрибуты сообщения."""

        if not isinstance(sender_id, UUID):
            raise InvalidMessageError("sender_id должен быть объектом UUID")

        if conversation_id is not None and not isinstance(conversation_id, UUID):
            raise InvalidMessageError("conversation_id должен быть UUID или None")

        if room_id is not None and not isinstance(room_id, UUID):
            raise InvalidMessageError("room_id должен быть UUID или None")

        if (conversation_id is None) == (room_id is None):
            raise InvalidMessageError(
                "Сообщение должно принадлежать либо переписке, либо комнате"
            )

        if not isinstance(text, str):
            raise InvalidMessageError("Текст сообщения должен быть строкой")

        return sender_id, conversation_id, room_id, text

    @classmethod
    def from_db(
        cls,
        id: str,
        created_at: str,
        sender_id: str,
        text: str,
        conversation_id: str | None = None,
        room_id: str | None = None,
    ) -> "Message":
        message_object = cls(
            sender_id=UUID(sender_id),
            text=text,
            conversation_id=(
                UUID(conversation_id) if conversation_id is not None else None
            ),
            room_id=UUID(room_id) if room_id is not None else None,
        )

        message_object.id = UUID(id)
        message_object.created_at = datetime.fromisoformat(created_at)

        return message_object
