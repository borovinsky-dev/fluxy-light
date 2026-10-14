from fluxy_light.database.database import Database
from fluxy_light.models.room import Room
from contextlib import closing
from uuid import UUID


class RoomRepo:

    def __init__(self, database: Database):
        if not isinstance(database, Database):
            raise TypeError("Database должен быть типом Database")

    def save_room(self, room: Room) -> None:
        if not isinstance(room, Room):
            raise TypeError("Room должен быть объектом класса Room")
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

    def get_by_id(self, room_id: UUID) -> Room | None:
        if not isinstance(room_id, UUID):
            raise TypeError("room_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT id, name, creator_id, is_moderated, created_at
                FROM rooms
                WHERE id = ?
                """,
                (str(room_id),),
            ).fetchone()

        if result is None:
            return None

        return Room.from_db(
            id=result[0],
            name=result[1],
            creator_id=result[2],
            is_moderated=result[3],
            created_at=result[4],
        )

    def exists_by_id(self, room_id: UUID) -> bool:
        if not isinstance(room_id, UUID):
            raise TypeError("room_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            result = connection.execute(
                """
                SELECT 1
                FROM rooms
                WHERE id = ?
                """,
                (str(room_id),),
            ).fetchone()

        return result is not None

    def get_by_creator_id(self, creator_id: UUID) -> list[Room]:
        if not isinstance(creator_id, UUID):
            raise TypeError("creator_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            results = connection.execute(
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
            for row in results
        ]
