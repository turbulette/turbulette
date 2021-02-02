from types import FunctionType
from typing import Type, Union
from pydantic import BaseModel, ValidationError
from ..errors import PydanticsValidationError


def validate(
    model: Type[BaseModel],
    input_kwarg: str = "input",
):
    """Validate input data using the given pydantic model.

    If a `ValueError` is raised during validation, the decorated resolver
    won't be called. Instead, the decorator will return a GraphQL response
    containing error messages from pydantic in the error field defined by the `ERROR_FIELD` setting.

    Args:
        model (Type[BaseModel]): The pydantic model used to validate data
        input_kwarg (str, optional): Name of the keyword argument that contains input data.
    """

    def wrap(func: FunctionType):
        async def wrapped_func(obj, info, **kwargs) -> Union[FunctionType, dict]:
            try:
                valid_input = model(**kwargs[input_kwarg]).dict()
                return await func(obj, info, valid_input, **kwargs)
            except ValidationError as exception:
                return PydanticsValidationError(exception).dict()

        return wrapped_func

    return wrap
