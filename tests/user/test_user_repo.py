import sqlite3
from datetime import datetime
from uuid import UUID

import pytest

from fluxy_light.database.database import Database
from fluxy_light.models.role import Role
from fluxy_light.models.user import User
from fluxy_light.repository.temp_exceptions import UserAlreadyExistsError
from fluxy_light.repository.user_repo import UserRepo


@pytest.fixture
def user_repo(tmp_path):
    db_path = tmp_path / "test_fluxy.db"

    # Создаём схему для изолированной тестовой БД.
    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

    database = Database(db_path)
    return UserRepo(database)


def test_save_user(user_repo):
    user = User("test_user")

    user_repo.save_user(user)

    restored_user = user_repo.get_user_by_id(user.id)

    assert restored_user is not None
    assert restored_user.id == user.id
    assert restored_user.username == user.username
    assert restored_user.role == user.role
    assert restored_user.created_at == user.created_at


def test_get_user_by_id_not_found(user_repo):
    user = user_repo.get_user_by_id(UUID("00000000-0000-0000-0000-000000000001"))

    assert user is None


def test_get_user_by_username(user_repo):
    user = User("username_test")
    user_repo.save_user(user)

    restored_user = user_repo.get_user_by_username("username_test")

    assert restored_user is not None
    assert restored_user.id == user.id
    assert restored_user.username == user.username


def test_get_user_by_username_not_found(user_repo):
    user = user_repo.get_user_by_username("missing_user")

    assert user is None


def test_get_all_users(user_repo):
    first_user = User("first_user")
    second_user = User("second_user")

    user_repo.save_user(first_user)
    user_repo.save_user(second_user)

    users = user_repo.get_all_users()

    assert len(users) == 2
    assert {user.username for user in users} == {
        "first_user",
        "second_user",
    }


def test_get_all_users_empty(user_repo):
    users = user_repo.get_all_users()

    assert users == []


def test_exists_by_username(user_repo):
    user = User("exists_user")
    user_repo.save_user(user)

    assert user_repo.exists_by_username("exists_user") is True
    assert user_repo.exists_by_username("missing_user") is False


def test_exists_by_id(user_repo):
    user = User("exists_id_user")
    user_repo.save_user(user)

    assert user_repo.exists_by_id(user.id) is True
    assert user_repo.exists_by_id(UUID("00000000-0000-0000-0000-000000000002")) is False


def test_delete_user_by_id(user_repo):
    user = User("delete_by_id")
    user_repo.save_user(user)

    user_repo.delete_user_by_id(user.id)

    assert user_repo.get_user_by_id(user.id) is None


def test_delete_user_by_username(user_repo):
    user = User("del_by_name")

    user_repo.save_user(user)
    user_repo.delete_user_by_username(user.username)

    assert user_repo.get_user_by_username(user.username) is None


def test_delete_missing_user_does_not_raise(user_repo):
    user_repo.delete_user_by_username("missing_user")
    user_repo.delete_user_by_id(UUID("00000000-0000-0000-0000-000000000003"))


def test_save_duplicate_username_raises(user_repo):
    first_user = User("duplicate_user")
    second_user = User("duplicate_user")

    user_repo.save_user(first_user)

    with pytest.raises(UserAlreadyExistsError):
        user_repo.save_user(second_user)


def test_repo_rejects_invalid_database():
    with pytest.raises(TypeError):
        UserRepo("not a database")
