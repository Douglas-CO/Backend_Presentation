from .custom_exception import CustomException


class CustomNetConnectException(CustomException):
    def __init__(self, message: str = "Error", data: dict = None, status: int = 400):
        super().__init__(message)
        self.data = data
        self.status = status
