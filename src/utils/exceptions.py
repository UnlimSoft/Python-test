from typing import Any


class BaseAPIException(Exception):
    def __init__(self, code: int, description: str):
        self.code = code
        self.detail = description


class ValueRequiredException(BaseAPIException):
    def __init__(self, *value_names: str):
        self.code = 1

        if len(value_names) > 1:
            values_str = ', '.join(['"' + value.__name__ + '"' for value in value_names])
            self.detail = f'Values {values_str} are required'
        else:
            self.detail = f'Value "{value_names[0]}" is required'


class ValueInvalidException(BaseAPIException):
    def __init__(self, value_name: str, description: str):
        self.code = 2
        self.detail = f'Value "{value_name}" is invalid: {description}'


class RecordDoesntExistException(BaseAPIException):
    def __init__(self, value_name: str, value: Any):
        self.code = 3
        self.detail = f'Record with given value ({value_name}={value}) does not exist'
