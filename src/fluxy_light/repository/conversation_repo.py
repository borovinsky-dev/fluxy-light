from contextlib import closing
from sqlite3 import IntegrityError
from uuid import UUID

from fluxy_light.database.database import Database
from fluxy_light.exceptions.repository import RepositoryIntegrityError
from fluxy_light.models.conversation import Conversation


class ConversationRepo:
    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("database должен быть объектом Database")

        self.database = database

    def save_conversation(self, conversation: Conversation) -> None:
        if not isinstance(conversation, Conversation):
            raise TypeError("conversation должен быть объектом Conversation")

        try:
            with closing(self.database.get_connection()) as connection:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO conversations (
                            id,
                            participant_1_id,
                            participant_2_id,
                            created_at
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            str(conversation.id),
                            str(conversation.ids[0]),
                            str(conversation.ids[1]),
                            conversation.created_at.isoformat(),
                        ),
                    )
        except IntegrityError as error:
            raise RepositoryIntegrityError(
                "Не удалось сохранить переписку: нарушено ограничение БД"
            ) from error

    def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        if not isinstance(conversation_id, UUID):
            raise TypeError("conversation_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT id, participant_1_id, participant_2_id, created_at
                FROM conversations
                WHERE id = ?
                """,
                (str(conversation_id),),
            ).fetchone()

        if result is None:
            return None

        return Conversation.from_db(
            id=result[0],
            participant_1_id=result[1],
            participant_2_id=result[2],
            created_at=result[3],
        )

    def get_between_users(
        self,
        user1_id: UUID,
        user2_id: UUID,
    ) -> Conversation | None:
        if not isinstance(user1_id, UUID) or not isinstance(user2_id, UUID):
            raise TypeError("ID пользователей должны быть объектами UUID")

        if user1_id == user2_id:
            raise ValueError("ID пользователей должны различаться")

        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT id, participant_1_id, participant_2_id, created_at
                FROM conversations
                WHERE
                    (participant_1_id = ? AND participant_2_id = ?)
                    OR
                    (participant_1_id = ? AND participant_2_id = ?)
                LIMIT 1
                """,
                (
                    str(user1_id),
                    str(user2_id),
                    str(user2_id),
                    str(user1_id),
                ),
            ).fetchone()

        if result is None:
            return None

        return Conversation.from_db(
            id=result[0],
            participant_1_id=result[1],
            participant_2_id=result[2],
            created_at=result[3],
        )

    def exists_by_id(self, conversation_id: UUID) -> bool:
        if not isinstance(conversation_id, UUID):
            raise TypeError("conversation_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT 1
                FROM conversations
                WHERE id = ?
                """,
                (str(conversation_id),),
            ).fetchone()

        return result is not None
