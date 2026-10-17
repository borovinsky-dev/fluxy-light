from contextlib import closing
from uuid import UUID
from datetime import datetime
from sqlite3 import IntegrityError

from fluxy_light.database.database import Database
from fluxy_light.models.user import User
from fluxy_light.exceptions.repository import UserAlreadyExistsError
from fluxy_light.models.role import Role


class UserRepo:

    def __init__(self, database: Database) -> None:
        if not isinstance(database, Database):
            raise TypeError("Должен быть объектом Database с подключением")
        self.database = database

    def save_user(self, user: User, password_salt, password_hash) -> None:
        if (
            self.exists_by_username(user.username)
            or self.exists_by_id(user.id)
            or self.exists_by_email(user.email)
        ):
            raise UserAlreadyExistsError(
                "Пользователь с таким ID, username или email уже существует"
            )
        try:
            with closing(self.database.get_connection()) as connection:
                with connection:
                    connection.execute(
                        """
                INSERT INTO users (
                    id,
                    username,
                    email,
                    password_salt,
                    password_hash,
                    role,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                        (
                            str(user.id),
                            user.username,
                            user.email,
                            password_salt,
                            password_hash,
                            user.role.value,
                            user.created_at.isoformat(),
                        ),
                    )
        except IntegrityError as error:
            if error.sqlite_errorname in {
                "SQLITE_CONSTRAINT_PRIMARYKEY",
                "SQLITE_CONSTRAINT_UNIQUE",
            }:
                raise UserAlreadyExistsError(
                    "Пользователь с таким ID, username или email уже существует"
                ) from error
            raise

    def get_user_by_username(self, username: str) -> None | User:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
            SELECT id, username, email, role, created_at
            FROM users
            WHERE username = ?
            """,
                    (str(username),),
                ).fetchone()
            if result is None:
                return None
            return User.from_db(
                user_id=UUID(result[0]),
                username=result[1],
                email=result[2],
                role=Role(result[3]),
                created_at=datetime.fromisoformat(result[4]),
            )

    def get_user_by_email(self, email: str) -> User:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                SELECT id, username, email, role, created_at
                FROM users
                WHERE email = ?
                """,
                    (email,),
                ).fetchone()
            if result is None:
                return None
            return User.from_db(
                user_id=UUID(result[0]),
                username=result[1],
                email=result[2],
                role=Role(result[3]),
                created_at=datetime.fromisoformat(result[4]),
            )

    def get_all_users(self) -> list[User]:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute("""
                SELECT id, username, email, role, created_at
                FROM users
                """).fetchall()
            if result is None:
                return None
            list_result = []
            for i in range(len(result)):
                user = User.from_db(
                    user_id=UUID(result[i][0]),
                    username=result[i][1],
                    email=result[i][2],
                    role=Role(result[i][3]),
                    created_at=datetime.fromisoformat(result[i][4]),
                )
                list_result.append(user)
            return list_result

    def get_user_by_id(self, user_id: UUID) -> None | User:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
            SELECT id, username, email, role, created_at
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
                email=result[2],
                role=Role(result[3]),
                created_at=datetime.fromisoformat(result[4]),
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

    def exists_by_email(self, email: str) -> bool:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    "SELECT 1 FROM users WHERE email = ?", (email,)
                ).fetchone()
                if result is not None:
                    return True
                else:
                    return False

    def delete_user_by_id(self, user_id: UUID) -> bool:
        if not isinstance(user_id, UUID):
            raise TypeError("user_id должен быть UUID")

        with closing(self.database.get_connection()) as connection:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM users WHERE id = ?",
                    (str(user_id),),
                )

        return cursor.rowcount > 0

    def delete_user_by_username(self, username: str) -> None:
        with closing(self.database.get_connection()) as connection:
            with connection:
                connection.execute(
                    """ DELETE FROM users WHERE username = ? """,
                    (username,),
                )

    def get_auth_by_email(self, email: str) -> tuple[User, bytes, bytes] | None:
        with closing(self.database.get_connection()) as connection:
            with connection:
                result = connection.execute(
                    """
                    SELECT
                        id, username, email, role, created_at,
                        password_salt, password_hash
                    FROM users
                    WHERE email = ?
                    """,
                    (email,),
                ).fetchone()

            if result is None:
                return None

            user = User.from_db(
                user_id=UUID(result[0]),
                username=result[1],
                email=result[2],
                role=Role(result[3]),
                created_at=datetime.fromisoformat(result[4]),
            )

            password_salt = result[5]
            password_hash = result[6]

        return user, password_salt, password_hash
