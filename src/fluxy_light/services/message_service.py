from uuid import UUID

from fluxy_light.repository.message_repo import MessageRepo
from fluxy_light.models.message import Message
from fluxy_light.repository.conversation_repo import ConversationRepo
from fluxy_light.repository.room_repo import RoomRepo


class MessageService:

    def __init__(
        self,
        message_repo: MessageRepo,
        conversation_repo: ConversationRepo,
        room_repo: RoomRepo,
    ) -> None:
        self.message_repo = message_repo
        self.conversation_repo = conversation_repo
        self.room_repo = room_repo

    def send_personal_message(
        self, sender_id: str, conversation_id: str, text: str
    ) -> Message:
        sender_id = UUID(sender_id)
        conversation_id = UUID(conversation_id)
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ValueError("Личная переписка не найдена")
        if sender_id not in conversation.ids:
            raise PermissionError("Пользователь не является участником переписки")

        message = Message(
            sender_id=sender_id,
            text=text,
            conversation_id=conversation_id,
        )

        self.message_repo.save_message(message)
        return message

    def send_room_message(
        self,
        sender_id: str,
        room_id: str,
        text: str,
    ) -> Message:

        sender_id = UUID(sender_id)
        room_id = UUID(room_id)
        user = self.user_repo.get_user_by_id(sender_id)

        if user is None:
            raise ValueError("Отправитель не найден")

        room = self.room_repo.get_room_by_id(room_id)
        if room is None:
            raise ValueError("Такой комнаты нет")

        message = Message(
            sender_id=sender_id,
            text=text,
            room_id=room_id,
        )

        self.message_repo.save_message(message)

        return message

    def get_personal_messages(
        self,
        conversation_id: str,
    ) -> list[Message]:
        return self.message_repo.get_messages_by_conversation_id(UUID(conversation_id))

    def get_room_messages(
        self,
        room_id: str,
    ) -> list[Message]:
        return self.message_repo.get_messages_by_room_id(UUID(room_id))
