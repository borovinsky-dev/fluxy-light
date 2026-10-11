import sqlite3 as sql


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get_connection(self) -> sql.Connection:
        return sql.connect(self.db_path)
