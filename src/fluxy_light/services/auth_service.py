from fluxy_light.services.user_service import UserService
from fluxy_light.services.password_service import PasswordService
from fluxy_light.models.user import User
from fluxy_light.exceptions.service import AuthenticationError


class AuthService:
    """Отвечает за вход и регистрацию"""

    def __init__(
        self, user_service: UserService, password_service: PasswordService
    ) -> None:
        self.user_service = user_service
        self.password_service = password_service

    def login(self, email: str, password: str) -> User:
        auth_data = self.user_repo.get_auth_data_by_email(email)

        if auth_data is None:
            raise AuthenticationError("Неверный email или пароль")

        user, password_salt, password_hash = auth_data

        if not self.password_service.verify_password(
            password,
            password_salt,
            password_hash,
        ):
            raise AuthenticationError("Неверный email или пароль")

        return user

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        user = self.user_service.create_user(
            username=username,
            email=email,
            password=password,
        )

        return user
