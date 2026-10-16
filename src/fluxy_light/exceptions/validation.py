from fluxy_light.exceptions.base import FluxyLightError


class ValidationError(FluxyLightError):
    """Базовое исключение для ошибок валидации."""


class InvalidUsernameError(ValidationError):
    """Вызывается, когда имя пользователя некорректно."""


class InvalidEmailError(ValidationError):
    """Вызывается, когда адрес электронной почты некорректен."""


class InvalidMessageError(ValidationError):
    """Вызывается, когда атрибуты сообщения некорректны."""


class InvalidConversationError(ValidationError):
    """Вызывается, когда атрибуты переписки некорректны."""


class InvalidRoomError(ValidationError):
    """Вызывается, когда атрибуты комнаты некорректны."""
