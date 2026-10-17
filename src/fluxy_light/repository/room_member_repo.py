from contextlib import closing
from sqlite3 import IntegrityError
from uuid import UUID

from fluxy_light.database.database import Database
from fluxy_light.models.room_member import RoomMember
from fluxy_light.exceptions.repository import RoomMemberAlreadyExistsError


class RoomMemberRepo:
    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("Должен быть объектом Database с подключением")
        self.database = database

    def save_member(self, room_member: RoomMember) -> None:
        """Добавление участника: сохраняет информацию о вступлении пользователя в
        комнату, включая его роль и время вступления."""
        try:
            with closing(self.database.get_connection()) as connection:
                with connection:
                    connection.execute(
                        """
                    INSERT INTO room_members (
                    room_id,
                    user_id,
                    role,
                    joined_at
                    )
                    VALUES (?, ?, ?, ?)
                """,
                        (
                            str(room_member.room_id),
                            str(room_member.user_id),
                            str(room_member.role),
                            room_member.joined_at.isoformat(),
                        ),
                    )
        except IntegrityError as error:
            if error.sqlite_errorname in {
                "SQLITE_CONSTRAINT_PRIMARYKEY",
                "SQLITE_CONSTRAINT_UNIQUE",
            }:
                raise RoomMemberAlreadyExistsError(
                    "Пользователь уже состоит в этой комнате"
                ) from error
            raise

    def get_member(
        self,
        room_id: UUID,
        user_id: UUID,
    ) -> RoomMember | None:
        """Получение участника: находит конкретного пользователя в определённой комнате."""
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                SELECT room_id, user_id, role, joined_at
                FROM room_members
                WHERE room_id = ? AND user_id = &
                """,
                    (str(room_id), str(user_id)),
                ).fetchone()
            if result is None:
                return None
            return RoomMember.from_db(*result)

    def get_room_members(self, room_id: UUID) -> list[RoomMember]:
        """Получение списка участников: возвращает всех пользователей,
        состоящих в указанной комнате."""
        with closing(self.database.get_connection()) as connection:
            results = connection.execute(
                """
                SELECT room_id, user_id, role, joined_at
                FROM room_members
                WHERE room_id = ?
                ORDER BY joined_at
                """,
                (str(room_id),),
            ).fetchall()

        return [RoomMember.from_db(*row) for row in results]

    def is_member(self, room_id: UUID, user_id: UUID) -> bool:
        """Проверка членства: определяет, состоит ли пользователь в комнате."""
        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT 1
                FROM room_members
                WHERE room_id = ? AND user_id = ?
                """,
                (str(room_id), str(user_id)),
            ).fetchone()

        return result is not None

    def update_role(
        self,
        room_id: UUID,
        user_id: UUID,
        role: str,
    ) -> bool:
        """Изменение роли: обновляет роль участника, например при назначении модератора."""
        if role not in ("owner", "moderator", "member"):
            raise ValueError("Недопустимая роль участника комнаты")

        with closing(self.database.get_connection()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE room_members
                    SET role = ?
                    WHERE room_id = ? AND user_id = ?
                    """,
                    (role, str(room_id), str(user_id)),
                )

        return cursor.rowcount > 0

    def delete_member(self, room_id: UUID, user_id: UUID) -> bool:
        """Удаление участника: удаляет связь между пользователем и комнатой,
        не удаляя самого пользователя или комнату."""
        with closing(self.database.get_connection()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    DELETE FROM room_members
                    WHERE room_id = ? AND user_id = ?
                    """,
                    (str(room_id), str(user_id)),
                )

        return cursor.rowcount > 0
