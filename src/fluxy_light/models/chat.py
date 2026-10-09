from datetime import datetime, timezone
from uuid import UUID, uuid4

from fluxy_light.models.user import User
from fluxy_light.models.room import Room


class Message:
    def __init__(
        self,
        author_message: User,
        message: str,
        room_id: Room = UUID | None,
        conversation_id: 
    ):
        self.id = uuid4()
        self.author_message = author_message
        self.message = message
        self.room_id = room_id
        self.created_at = datetime.now(timezone.utc)
