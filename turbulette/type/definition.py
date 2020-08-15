from typing import Any, Dict, Union
from starlette.config import Config


DatabaseSettings = Dict[str, Union[Config, str]]
