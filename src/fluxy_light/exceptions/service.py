from fluxy_light.exceptions.base import FluxyLightError


class ServiceError(FluxyLightError):
    """Базовое исключение сервисного слоя."""


class UserNotFoundError(ServiceError):
    """Пользователь не найден."""
