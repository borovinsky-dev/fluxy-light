from uuid import uuid4

from fluxy_light.database.database import Database
from fluxy_light.exceptions.service import UserNotFoundError
from fluxy_light.repository.user_repo import UserRepo
from fluxy_light.services.password_service import PasswordService
from fluxy_light.services.user_service import UserService


def main() -> None:
    database = Database()
    database.initialize()

    user_repo = UserRepo(database)
    password_service = PasswordService()
    user_service = UserService(user_repo, password_service)

    password = "TestPassword123!"

    username = f"test_{uuid4().hex[:8]}"
    email = f"{username}@example.com"

    print("1. Тестирую регистрацию пользователя")
    user = user_service.create_user(username, email, password)

    assert user.id is not None
    assert user.username == username
    assert user.email == email
    print("Успешно: пользователь создан")
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")

    print("\n2. Тестирую поиск по ID")
    found_user = user_service.get_user_by_id(str(user.id))

    assert found_user is not None
    assert found_user.id == user.id
    print("Успешно: пользователь найден по ID")

    print("\n3. Тестирую поиск по username")
    found_user = user_service.get_user_by_username(username)

    assert found_user is not None
    assert found_user.username == username
    print("Успешно: пользователь найден по username")

    print("\n4. Тестирую получение списка пользователей")
    users = user_service.get_all_users()

    assert any(existing_user.id == user.id for existing_user in users)
    print(f"Успешно: получен список из {len(users)} пользователей")

    print("\n5. Тестирую сохранение хеша пароля")

    with database.get_connection() as connection:
        row = connection.execute(
            """
            SELECT password_salt, password_hash
            FROM users
            WHERE id = ?
            """,
            (str(user.id),),
        ).fetchone()

    assert row is not None

    password_salt, password_hash = row

    assert password_salt is not None
    assert password_hash is not None

    assert password_service.verify_password(
        password,
        password_salt,
        password_hash,
    )
    assert not password_service.verify_password(
        "WrongPassword123!",
        password_salt,
        password_hash,
    )

    print("Успешно: соль и хеш сохранены, пароль проверяется")

    print("\n6. Тестирую удаление по username")
    user_service.delete_user_by_username(username)

    assert user_service.get_user_by_id(str(user.id)) is None
    print("Успешно: пользователь удалён по username")

    print("\n7. Тестирую удаление отсутствующего пользователя по ID")
    try:
        user_service.delete_user_by_id(str(uuid4()))
    except UserNotFoundError:
        print("Успешно: UserNotFoundError получен")
    else:
        raise AssertionError(
            "Ожидалось UserNotFoundError при удалении отсутствующего ID"
        )

    print("\n8. Тестирую удаление отсутствующего пользователя по username")
    missing_username = f"missing_{uuid4().hex[:8]}"

    try:
        user_service.delete_user_by_username(missing_username)
    except UserNotFoundError:
        print("Успешно: UserNotFoundError получен")
    else:
        raise AssertionError(
            "Ожидалось UserNotFoundError при удалении отсутствующего username"
        )

    print("\n9. Тестирую поиск отсутствующего пользователя")
    missing_user = user_service.get_user_by_username(missing_username)

    assert missing_user is None
    print("Успешно: поиск возвращает None")

    print("\n10. Тестирую некорректный UUID")
    try:
        user_service.get_user_by_id("invalid-uuid")
    except ValueError:
        print("Успешно: некорректный UUID отклонён")
    else:
        raise AssertionError("Ожидался ValueError для некорректного UUID")

    print("\n11. Тестирую удаление по ID")
    second_username = f"test_{uuid4().hex[:8]}"
    second_email = f"{second_username}@example.com"

    second_user = user_service.create_user(
        second_username,
        second_email,
        password,
    )

    # Убеждаемся, что пользователь действительно сохранён.
    assert user_service.get_user_by_id(str(second_user.id)) is not None

    user_service.delete_user_by_id(str(second_user.id))

    # Проверяем результат удаления.
    assert user_service.get_user_by_id(str(second_user.id)) is None

    print("Успешно: пользователь удалён по ID")

    print("\nВсе 11 проверок успешно пройдены!")


if __name__ == "__main__":
    main()
