from types import FunctionType
from typing import Optional, Union
from pydantic import BaseModel, ValidationError
from ..errors import PydanticsValidationError


def validate(
    model: Optional[BaseModel] = None,
    models: [BaseModel] = None,
    input_kwarg: str = "input",
):
    def wrap(func: FunctionType):
        async def wrapped_func(obj, info, **kwargs) -> Union[FunctionType, dict]:
            try:
                if models:
                    valid_input = [
                        model_(**kwargs[input_kwarg]).dict() for model_ in models
                    ]
                else:
                    valid_input = model(**kwargs[input_kwarg]).dict()
                return await func(obj, info, valid_input, **kwargs)
            except ValidationError as exception:
                return PydanticsValidationError(exception).dict()

        return wrapped_func

    return wrap
