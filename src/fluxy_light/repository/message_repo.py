from contextlib import closing
from uuid import UUID
from datetime import datetime
import os

from fluxy_light.database.database import Database
from fluxy_light.models.message import Message


class MessageRepo:
    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("Должен быть объектом Database с подключением")
        self.database = database

    def save_message(self, message: Message) -> None:
        if not isinstance(message, Message):
            raise TypeError("Message должен быть объектом класса Message")

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
                            if message.conversation_id
                            else None
                        ),
                        str(message.room_id) if message.room_id else None,
                        message.text,
                        message.created_at.isoformat(),
                    ),
                )

    def get_message_by_id(self, message_id: UUID) -> Message | None:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                    SELECT id, sender_id, conversation_id, room_id, text, created_at
                    FROM messages
                    WHERE id = ?
                    """,
                    (str(message_id),),
                ).fetchone()
            if result is None:
                return None
            print(result)
            return Message.from_db(
                id=result[0],
                sender_id=result[1],
                conversation_id=result[2],
                room_id=result[3],
                text=result[4],
                created_at=result[5],
            )

    def get_messages_by_conversation_id(self, conversation_id: UUID) -> list[Message]:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                    SELECT id, sender_id, conversation_id, room_id, text, created_at
                    FROM messages
                    WHERE conversation_id = ?
                    """,
                    (str(conversation_id),),
                ).fetchall()
            list_result = []
            for row in result:
                message = Message.from_db(
                    id=row[0],
                    sender_id=row[1],
                    conversation_id=row[2],
                    room_id=row[3],
                    text=row[4],
                    created_at=row[5],
                )
                list_result.append(message)
            return list_result

    def get_messages_by_room_id(self, room_id: UUID) -> list[Message]:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                SELECT id, sender_id, conversation_id, room_id, text, created_at
                FROM messages
                WHERE room_id = ?
                """,
                    (str(room_id),),
                ).fetchall()
            list_result = []
            for row in result:
                message = Message.from_db(
                    id=row[0],
                    sender_id=row[1],
                    conversation_id=row[2],
                    room_id=row[3],
                    text=row[4],
                    created_at=row[5],
                )
                list_result.append(message)
            return list_result


def main() -> None:
    print("1. Вошли в main()", flush=True)

    database = Database()
    print("2. Database создан", flush=True)

    database.initialize()
    print("3. База инициализирована", flush=True)

    message_repo = MessageRepo(database)
    print("4. MessageRepo создан", flush=True)

    with closing(database.get_connection()) as connection:
        user = connection.execute("SELECT id FROM users LIMIT 1").fetchone()

        conversation = connection.execute(
            "SELECT id FROM conversations LIMIT 1"
        ).fetchone()

        room = connection.execute("SELECT id FROM rooms LIMIT 1").fetchone()

    print("5. Запросы выполнены", flush=True)
    print("Пользователь:", user, flush=True)
    print("Переписка:", conversation, flush=True)
    print("Комната:", room, flush=True)


if __name__ == "__main__":
    filename = os.path.basename(__file__)
    print(f"Тестирование модуля {filename}")
    print("Вызываю main()")
    main()
    print("main() завершился")
