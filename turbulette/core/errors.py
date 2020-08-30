class BaseError:
    """Base error class used to return functional errors.
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


class PermissionDenied(BaseError):
    """Wrap BaseError with a default message for permission errors.

    Args:
        BaseError (class): Inherits from BaseError class
    """

    def __init__(self, message="You are not allowed to perform this action"):
        super().__init__(message=message)


class PydanticsValidationError(BaseError):
    """Handle pydantic error messages when trying to validate a model.

    Args:
        BaseError (class): Inherits from BaseError class
    """

    def __init__(self, exception):
        out = [f"{', '.join(e['loc'])}: {e['msg']}" for e in exception.errors()]
        super().__init__(errors_list=out)
