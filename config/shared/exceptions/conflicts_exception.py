from .custom_exception import CustomException


class ConflictsException(CustomException):
    def __init__(self, message: str, data: object):
        super().__init__(message)
        self.data = data
