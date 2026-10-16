from hashlib import scrypt
from hmac import compare_digest
from secrets import token_bytes


class PasswordService:
    """Сервис для хеширования и проверки паролей."""

    @staticmethod
    def hash_password(password: str) -> tuple[bytes, bytes]:
        if not isinstance(password, str):
            raise TypeError("Пароль должен быть строкой")

        if not password:
            raise ValueError("Пароль не должен быть пустым")

        password_salt = token_bytes(16)

        password_hash = scrypt(
            password.encode("utf-8"),
            salt=password_salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )

        return password_salt, password_hash

    @staticmethod
    def verify_password(
        password: str,
        password_salt: bytes,
        expected_hash: bytes,
    ) -> bool:
        if not isinstance(password, str):
            raise TypeError("Пароль должен быть строкой")

        if not password:
            raise ValueError("Пароль не должен быть пустым")

        if not isinstance(password_salt, bytes):
            raise TypeError("Соль должна иметь тип bytes")

        if not password_salt:
            raise ValueError("Соль не должна быть пустой")

        if not isinstance(expected_hash, bytes):
            raise TypeError("Хеш должен иметь тип bytes")

        if not expected_hash:
            raise ValueError("Хеш не должен быть пустым")

        password_hash = scrypt(
            password.encode("utf-8"),
            salt=password_salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64,
        )

        return compare_digest(password_hash, expected_hash)
