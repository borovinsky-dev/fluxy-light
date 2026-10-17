from uuid import UUID

from fluxy_light.exceptions.service import UserNotFoundError
from fluxy_light.models.user import User
from fluxy_light.repository.user_repo import UserRepo
from fluxy_light.services.password_service import PasswordService


class UserService:
    def __init__(
        self,
        user_repo: UserRepo,
        password_service: PasswordService,
    ) -> None:
        self.user_repo = user_repo
        self.password_service = password_service

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        user = User(email=email, username=username)

        password_salt, password_hash = self.password_service.hash_password(password)

        self.user_repo.save_user(
            user,
            password_salt,
            password_hash,
        )

        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.user_repo.get_user_by_id(UUID(user_id))

    def get_user_by_username(self, username: str) -> User | None:
        return self.user_repo.get_user_by_username(username)

    def get_user_by_email(self, email: str) -> User | None:
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self) -> list[User]:
        return self.user_repo.get_all_users()

    def delete_user_by_id(self, user_id: str) -> None:
        deleted = self.user_repo.delete_user_by_id(UUID(user_id))

        if not deleted:
            raise UserNotFoundError(f"Пользователь с ID {user_id} не найден")

    def delete_user_by_username(self, username: str) -> None:
        user = self.user_repo.get_user_by_username(username)

        if user is None:
            raise UserNotFoundError(f"Пользователь с username {username!r} не найден")

        self.user_repo.delete_user_by_id(user.id)
