from enum import Enum


# создание других пользователей в будущем
class Role(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
