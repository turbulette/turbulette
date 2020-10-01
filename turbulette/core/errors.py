from enum import Enum
from typing import Dict, List
from ariadne import format_error
from graphql import GraphQLError
from turbulette import conf

errors: Dict[str, Dict[str, List]] = {}


class ErrorCode(Enum):
    """Store error codes as names and messages as values.

    It is intended to be used with `BaseError` Exception and it subclasses
    to provide consistent formatting in GraphQL error responses.
    """

    JWT_EXPIRED = "JWT has expired"
    JWT_INVALID_SINATURE = "JWT signature cannot be validated"
    JWT_INVALID = "JWT is invalid and/or improperly formatted"
    JWT_USERNAME_NOT_FOUND = "No username was found when decoding the JWT"
    JWT_INVALID_PREFIX = "JWT prefix in the authorization header is invalid"
    JWT_NOT_FOUND = "JWT was not found"
    JWT_NOT_FRESH = "JWT is not fresh enough"
    JWT_INVALID_TOKEN_TYPE = "JWT type is invalid"
    FIELD_NOT_ALLOWED = "Some fields are not allowed"
    SERVER_ERROR = "Internal server error"
    QUERY_NOT_ALLOWED = "You are not allowed to perform this query"
    JWE_INVALID_TOKEN = "JWE token is invalid"
    JWE_DECRYPTION_ERROR = "JWE payload can't be decrypted or object is malformed"


class BaseError(Exception):
    """Base Exception class for unexpected server errors."""

    error_code: Enum = ErrorCode.SERVER_ERROR
    extensions: dict = {}

    def __init__(self, message: str = None):
        self.extensions["code"] = self.error_code.name
        if not message:
            message = self.error_code.value
        super().__init__(message)


class ErrorField:
    """Base error class used to return functional errors.
    intended for the end user in a dedicated field
    """

    def __init__(
        self, message: str = None, nature: str = None, errors_list: list = None
    ):
        if errors_list:
            self.errors_list = errors_list
        elif message:
            self.errors_list = [f"{nature}: {message}"] if nature else [message]
        else:
            self.errors_list = []

    def dict(self) -> dict:
        return {conf.settings.ERROR_FIELD: self.errors_list}

    def __str__(self) -> str:
        """Format errors array to a string."""
        return "\n".join(self.errors_list)

    def add(self, message: str, nature: str = None):
        self.errors_list.append(f"{nature}: {message}" if nature else message)


class PydanticsValidationError(ErrorField):
    """Handle pydantic error messages when trying to validate a model.

    Args:
        BaseError (class): Inherits from BaseError class
    """

    def __init__(self, exception):
        out = [f"{', '.join(e['loc'])}: {e['msg']}" for e in exception.errors()]
        super().__init__(errors_list=out)


def error_formatter(error: GraphQLError, debug: bool = False):
    """Replace Ariadne default error formatter.

    Args:
        error (GraphQLError): The GraphQL error
        debug (bool, optional): True if ASGI app has been
            instantiated with debug=True. Defaults to False.

    Returns:
        dict: [description]
    """
    if debug:
        # If debug is enabled, reuse Ariadne's formatting logic
        formatted = format_error(error, debug)
    else:
        formatted = error.formatted  # pragma: no cover

    return formatted


def add_error(err_type: str, code: ErrorCode, message: str = None):
    if not message:
        message = code.value
    if err_type not in errors:
        errors[err_type] = {code.name: [message]}
    elif code.name in errors[err_type] and message not in errors[err_type][code.name]:
        errors[err_type][code.name].append(message)
