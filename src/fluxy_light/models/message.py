from datetime import datetime, timezone
from uuid import UUID, uuid4

from fluxy_light.models.user import User
from fluxy_light.models.room import Room


class Message:
    def __init__(
        self,
        sender_id: UUID,
        text: str,
        conversation_id: UUID | None = None,
        room_id: UUID | None = None,
    ):
        self.id = uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.sender_id, self.conversation_id, self.room_id, self.text = (
            self.validate_attributes(sender_id, conversation_id, room_id, text)
        )

    # валидация проходит с распоковкой кортежа в будущем
    @staticmethod
    def validate_attributes(
        sender_id: UUID | None,
        conversation_id: UUID | None,
        room_id: UUID | None,
        text: str,
    ) -> tuple[UUID, UUID | None, UUID | None, str]:
        """Поле sender_id будет обязательное, но поля conversation_id и room_id не будут обязательными"""
        if (
            (type(sender_id) != UUID)
            or (type(conversation_id) != UUID and conversation_id is not None)
            or (type(room_id) != UUID and room_id is not None)
        ):
            raise TypeError("Недопустимые типы ID")
        if (conversation_id is None) == (room_id is None):
            raise ValueError(
                "Сообщение должно принадлежать либо переписке, либо комнате"
            )
        if type(text) != str:
            raise TypeError("Месседж должен быть текстом")

        return (sender_id, conversation_id, room_id, text)
