from .enums import ErrorCodes


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