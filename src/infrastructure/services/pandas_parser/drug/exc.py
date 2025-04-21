from src.utils.exc import BaseSystemException, ErrorCodes


class MissingPreExecutionError(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.UNKNOWN


class InvalidParsedData(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.UNKNOWN


class InvalidFileFormat(BaseSystemException):
    def __init__(self, message: str):
        self.message = message
        self.reason = ErrorCodes.UNKNOWN
