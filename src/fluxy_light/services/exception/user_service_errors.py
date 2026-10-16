class UserNotFoundError(Exception):

    def __init__(self, message: str, user_id: str, username: str) -> None:
        super().__init__(message)
        self.userame = username
