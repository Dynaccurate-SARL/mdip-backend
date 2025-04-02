from sqlalchemy import Enum


class ErrorCodes(str, Enum):
    NOT_FOUND = 'NOT_FOUND'
    ENTITY_NOT_FOUND = 'ENTITY_NOT_FOUND'
    DATA_EXISTS = 'DATA_EXISTS'
    NAME_ALREADY_IN_USE = 'NAME_ALREADY_IN_USE'
    RESOURCE_STILL_PROCESSING = 'RESOURCE_STILL_PROCESSING'
    LEDGER_ERROR = 'LEDGER_ERROR'


class BaseSystemException(Exception):
    message: str
    reason: ErrorCodes

    def __init__(self, message: str, reason: ErrorCodes):
        self.message = message
        self.reason = reason

    def __str__(self):
        return f'{self.message}'


class ForeignKeyResourseNotFound(BaseSystemException):
    pass


class ResourseNotFound(BaseSystemException):
    pass


class ConflictErrorCode(BaseSystemException):
    pass


class ResourceAlreadyExists(BaseSystemException):
    pass


class ResourceNotReady(BaseSystemException):
    pass


class BadRequest(BaseSystemException):
    pass


class UnauthorizedAccessError(BaseSystemException):
    pass