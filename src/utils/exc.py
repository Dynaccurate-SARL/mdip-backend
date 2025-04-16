from sqlalchemy import Enum
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ErrorCodes(str, Enum):
    UNAUTHORIZED = 'UNAUTHORIZED'
    NOT_FOUND = 'NOT_FOUND'
    ENTITY_NOT_FOUND = 'ENTITY_NOT_FOUND'
    NAME_ALREADY_IN_USE = 'NAME_ALREADY_IN_USE'
    CENTRAL_CATALOG_ALREADY_EXISTS = 'CENTRAL_CATALOG_ALREADY_EXISTS'
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

    def as_response(self, status_code: int):
        return JSONResponse(
            status_code=status_code,
            content={
                'detail': self.message
            },
            headers={
                'X-Reason': self.reason
            }
        )

    def as_http_exception(self, status_code: int):
        raise HTTPException(
            status_code=status_code,
            detail=self.message,
            headers={
                'X-Reason': self.reason
            }
        )


class ForeignKeyResourseNotFound(BaseSystemException):
    pass


class ResourseNotFound(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.ENTITY_NOT_FOUND


class ConflictErrorCode(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.CENTRAL_CATALOG_ALREADY_EXISTS


class ResourceAlreadyExists(BaseSystemException):
    pass


class ResourceNotReady(BaseSystemException):
    pass


class BadRequest(BaseSystemException):
    pass


class UnauthorizedAccessError(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.UNAUTHORIZED
