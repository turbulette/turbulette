from types import FunctionType
from typing import Union
from pydantic import BaseModel, ValidationError
from ..errors import PydanticsValidationError


def validate(
    model: BaseModel = None, models: [BaseModel] = None, input_kwarg: str = "input"
) -> FunctionType:
    def wrap(func: FunctionType) -> FunctionType:
        async def wrapped_func(obj, info, **kwargs) -> FunctionType:
            try:
                if models:
                    valid_input = [
                        model(**kwargs[input_kwarg]).dict() for model in models
                    ]
                else:
                    valid_input = model(**kwargs[input_kwarg]).dict()
                return await func(obj, info, valid_input, **kwargs)
            except ValidationError as exception:
                return PydanticsValidationError(exception).dict()

        return wrapped_func

    return wrap
