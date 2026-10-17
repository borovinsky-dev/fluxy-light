from fluxy_light.exceptions.base import FluxyLightError


class RepositoryError(FluxyLightError):
    """Base exception for repository errors."""


class UserAlreadyExistsError(RepositoryError):
    """Пользователь с таким ID, username или email уже существует."""


class RepositoryIntegrityError(RepositoryError):
    """Ошибка при нарушении ограничения базы данных."""


class RoomMemberAlreadyExistsError(Exception):
    pass
