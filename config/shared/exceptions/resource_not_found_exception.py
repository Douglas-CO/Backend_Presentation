from .custom_exception import CustomException


class ResourceNotFoundException(CustomException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
