from typing import List, Dict

from .custom_exception import CustomException

class InvalidFieldsException(CustomException):
    def __init__(self, message: str, fields: Dict[str, List[str]]):
        super().__init__(message)
        self.fields = fields
