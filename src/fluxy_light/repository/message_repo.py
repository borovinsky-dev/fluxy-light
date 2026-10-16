from contextlib import closing
from sqlite3 import IntegrityError
from uuid import UUID

from fluxy_light.database.database import Database
from fluxy_light.exceptions.repository import RepositoryIntegrityError
from fluxy_light.models.message import Message


class MessageRepo:
    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("database должен быть объектом Database")

        self.database = database

    def save_message(self, message: Message) -> None:
        if not isinstance(message, Message):
            raise TypeError("message должен быть объектом Message")

        try:
            with closing(self.database.get_connection()) as connection:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO messages (
                            id,
                            sender_id,
                            conversation_id,
                            room_id,
                            text,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(message.id),
                            str(message.sender_id),
                            (
                                str(message.conversation_id)
                                if message.conversation_id is not None
                                else None
                            ),
                            (
                                str(message.room_id)
                                if message.room_id is not None
                                else None
                            ),
                            message.text,
                            message.created_at.isoformat(),
                        ),
                    )
        except IntegrityError as error:
            raise RepositoryIntegrityError(
                "Не удалось сохранить сообщение: нарушено ограничение БД"
            ) from error

    def get_message_by_id(self, message_id: UUID) -> Message | None:
        if not isinstance(message_id, UUID):
            raise TypeError("message_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            row = connection.execute(
                """
                SELECT id, sender_id, conversation_id, room_id, text, created_at
                FROM messages
                WHERE id = ?
                """,
                (str(message_id),),
            ).fetchone()

        if row is None:
            return None

        return Message.from_db(
            id=row[0],
            sender_id=row[1],
            conversation_id=row[2],
            room_id=row[3],
            text=row[4],
            created_at=row[5],
        )

    def get_messages_by_conversation_id(
        self,
        conversation_id: UUID,
    ) -> list[Message]:
        if not isinstance(conversation_id, UUID):
            raise TypeError("conversation_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            rows = connection.execute(
                """
                SELECT id, sender_id, conversation_id, room_id, text, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at, id
                """,
                (str(conversation_id),),
            ).fetchall()

        return [
            Message.from_db(
                id=row[0],
                sender_id=row[1],
                conversation_id=row[2],
                room_id=row[3],
                text=row[4],
                created_at=row[5],
            )
            for row in rows
        ]

    def get_messages_by_room_id(self, room_id: UUID) -> list[Message]:
        if not isinstance(room_id, UUID):
            raise TypeError("room_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            rows = connection.execute(
                """
                SELECT id, sender_id, conversation_id, room_id, text, created_at
                FROM messages
                WHERE room_id = ?
                ORDER BY created_at, id
                """,
                (str(room_id),),
            ).fetchall()

        return [
            Message.from_db(
                id=row[0],
                sender_id=row[1],
                conversation_id=row[2],
                room_id=row[3],
                text=row[4],
                created_at=row[5],
            )
            for row in rows
        ]
