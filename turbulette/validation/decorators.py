from types import FunctionType
from typing import Type, Union
from pydantic import BaseModel, ValidationError
from ..errors import PydanticsValidationError


def validate(
    model: Type[BaseModel],
    input_kwarg: str = "input",
):
    def wrap(func: FunctionType):
        async def wrapped_func(obj, info, **kwargs) -> Union[FunctionType, dict]:
            try:
                valid_input = model(**kwargs[input_kwarg]).dict()
                return await func(obj, info, valid_input, **kwargs)
            except ValidationError as exception:
                return PydanticsValidationError(exception).dict()

        return wrapped_func

    return wrap
