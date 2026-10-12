from pathlib import Path
from contextlib import closing
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "Data" / "fluxy.db"


class Database:
    """Управление подключениями и инициализацией SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    # создание первичных таблиц
    def initialize(self) -> None:
        with closing(self.get_connection()) as connection:
            with connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT NOT NULL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        role TEXT NOT NULL
                            CHECK (role IN ('admin', 'moderator', 'member')),
                        created_at TEXT NOT NULL
                    )
                """)

                connection.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT NOT NULL PRIMARY KEY,
                        participant_1_id TEXT NOT NULL,
                        participant_2_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,

                        CHECK (participant_1_id != participant_2_id),

                        FOREIGN KEY (participant_1_id) REFERENCES users(id),
                        FOREIGN KEY (participant_2_id) REFERENCES users(id)
                    )
                """)

                connection.execute("""
                    CREATE TABLE IF NOT EXISTS rooms (
                        id TEXT NOT NULL PRIMARY KEY,
                        name TEXT NOT NULL,
                        creator_id TEXT NOT NULL,
                        is_moderated INTEGER NOT NULL
                            CHECK (is_moderated IN (0, 1)),
                        created_at TEXT NOT NULL,

                        FOREIGN KEY (creator_id) REFERENCES users(id)
                    )
                """)

                connection.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT NOT NULL PRIMARY KEY,
                        sender_id TEXT NOT NULL,
                        conversation_id TEXT,
                        room_id TEXT,
                        text TEXT NOT NULL,
                        created_at TEXT NOT NULL,

                        CHECK (
                            (conversation_id IS NOT NULL AND room_id IS NULL)
                            OR
                            (conversation_id IS NULL AND room_id IS NOT NULL)
                        ),

                        FOREIGN KEY (sender_id) REFERENCES users(id),
                        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                        FOREIGN KEY (room_id) REFERENCES rooms(id)
                    )
                """)
