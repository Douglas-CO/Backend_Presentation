from .custom_exception import CustomException


class UnauthorizedException(CustomException):
    def __init__(self, message: str = "Unauthorized", data: dict = None):
        super().__init__(message)
        self.data = data
