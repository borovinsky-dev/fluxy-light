from contextlib import closing
from sqlite3 import IntegrityError
from uuid import UUID

from fluxy_light.database.database import Database
from fluxy_light.exceptions.repository import (
    RepositoryIntegrityError,
    UserAlreadyExistsError,
)
from fluxy_light.models.room import Room


class RoomRepo:
    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("database должен быть объектом Database")

        self.database = database

    def save_room(self, room: Room) -> None:
        if not isinstance(room, Room):
            raise TypeError("room должен быть объектом Room")

        try:
            with closing(self.database.get_connection()) as connection:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO rooms (
                            id,
                            name,
                            creator_id,
                            is_moderated,
                            created_at
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            str(room.id),
                            room.name,
                            str(room.creator_id),
                            int(room.is_moderated),
                            room.created_at.isoformat(),
                        ),
                    )
        except IntegrityError as error:
            raise RepositoryIntegrityError(
                "Не удалось сохранить комнату: нарушено ограничение БД"
            ) from error

    def get_room_by_id(self, room_id: UUID) -> Room | None:
        if not isinstance(room_id, UUID):
            raise TypeError("room_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            row = connection.execute(
                """
                SELECT id, name, creator_id, is_moderated, created_at
                FROM rooms
                WHERE id = ?
                """,
                (str(room_id),),
            ).fetchone()

        if row is None:
            return None

        return Room.from_db(
            id=row[0],
            name=row[1],
            creator_id=row[2],
            is_moderated=row[3],
            created_at=row[4],
        )

    def exists_by_id(self, room_id: UUID) -> bool:
        if not isinstance(room_id, UUID):
            raise TypeError("room_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            row = connection.execute(
                "SELECT 1 FROM rooms WHERE id = ?",
                (str(room_id),),
            ).fetchone()

        return row is not None

    def get_by_creator_id(self, creator_id: UUID) -> list[Room]:
        if not isinstance(creator_id, UUID):
            raise TypeError("creator_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            rows = connection.execute(
                """
                SELECT id, name, creator_id, is_moderated, created_at
                FROM rooms
                WHERE creator_id = ?
                ORDER BY created_at
                """,
                (str(creator_id),),
            ).fetchall()

        return [
            Room.from_db(
                id=row[0],
                name=row[1],
                creator_id=row[2],
                is_moderated=row[3],
                created_at=row[4],
            )
            for row in rows
        ]
