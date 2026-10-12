from contextlib import closing
from uuid import UUID
from datetime import datetime

from fluxy_light.database.database import Database
from fluxy_light.models.user import User
from fluxy_light.repository.temp_exceptions import UserAlreadyExistsError
from fluxy_light.models.role import Role


class UserRepo:

    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("Должен быть объектом DataBase с подключением")
        self.database = database

    def save_user(self, user: User) -> None:
        if self.exists_by_username(user.username) or self.exists_by_id(user.id):
            raise UserAlreadyExistsError(
                "Пользователь с таким ID или username уже существует"
            )

        with closing(self.database.get_connection()) as connection:
            with connection:
                connection.execute(
                    """
            INSERT INTO users (id, username, role, created_at)
            VALUES (?, ?, ?, ?)
            """,
                    (
                        str(user.id),
                        user.username,
                        user.role.value,
                        user.created_at.isoformat(),
                    ),
                )

    def get_user_by_id(self, user_id: UUID) -> None | User:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
            SELECT id, username, role, created_at
            FROM users
            WHERE id = ?
            """,
                    (str(user_id),),
                ).fetchone()
            if result is None:
                return None
            return User.from_db(
                user_id=UUID(result[0]),
                username=result[1],
                role=Role(result[2]),
                created_at=datetime.fromisoformat(result[3]),
            )

    def exists_by_username(self, username: str) -> bool:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    "SELECT 1 FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
                if result is not None:
                    return True
                else:
                    return False

    def exists_by_id(self, id: UUID) -> bool:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    "SELECT 1 FROM users WHERE id = ?",
                    (str(id),),
                ).fetchone()
                if result is not None:
                    return True
                else:
                    return False


def main() -> None:

    database = Database()
    user_repo = UserRepo(database)

    user = User()

    # user_repo.save_user(user)

    user = User("test_user_123")

    user_repo.save_user(user)

    restored_user = user_repo.get_user_by_id(user.id)

    print(restored_user)
    print(user is restored_user)
    print(user.id == restored_user.id)


if __name__ == "__main__":
    print("Прямой запуск")
    main()
