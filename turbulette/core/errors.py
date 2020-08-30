from enum import Enum
from typing import Optional
from ariadne import format_error
from graphql import GraphQLError


class ErrorCode(Enum):
    """ Store error codes as names and messages as values

    It is intended to be used with `BaseError` Exception and it subclasses
    to provide consistent formatting in GraphQL error responses.
    """

    JWT_EXPIRED = "JWT has expired"
    JWT_INVALID_SINATURE = "JWT signature cannot be validated"
    JWT_INVALID = "JWT is invalid and/or improperly formatted"
    JWT_USERNAME_NOT_FOUND = "No username was found when decoding the JWT"
    JWT_INVALID_PREFIX = "JWT prefix in the authorization header is invalid"
    JWT_NOT_FOUND = "JWT was not found"
    JWT_INVALID_TOKEN_TYPE = "JWT type is invalid"


class BaseError(Exception):
    """Base Exception class for unexpected server errors
    """

    error_code: Optional[ErrorCode] = None
    extensions = {}

    def __init__(self, message: str = None):
        self.extensions["code"] = self.error_code.name
        super().__init__(message)


class ErrorField:
    """Base error class used to return functional errors
    intended for the end user in a dedicated field
    """

    errors_field_name = "errors"

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
        return {self.errors_field_name: self.errors_list}

    def __str__(self) -> str:
        """Format errors array to a string."""
        return "\n".join(self.errors_list)

    def add(self, message: str, nature: str = None):
        self.errors_list.append(f"{nature}: {message}" if nature else message)


class PermissionDenied(ErrorField):
    """Wrapp BaseError with a default message for permission errors

    Args:
        BaseError (class): Inherits from BaseError class
    """

    def __init__(self, message="You are not allowed to perform this action"):
        super().__init__(message=message)


class PydanticsValidationError(ErrorField):
    """Handle pydantic error messages when trying to validate a model

    Args:
        BaseError (class): Inherits from BaseError class
    """

    def __init__(self, exception):
        out = [f"{', '.join(e['loc'])}: {e['msg']}" for e in exception.errors()]
        super().__init__(errors_list=out)


def error_formatter(error: GraphQLError, debug: bool = False) -> dict:
    """Replace Ariadne default error formatter

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

    # Create formatted error data
    if "code" in formatted["extensions"]:
        for err in ErrorCode:
            if formatted["extensions"]["code"] == err.name:
                if not formatted.get("message") or formatted["message"] == "None":
                    formatted["message"] = err.value
    return formatted
