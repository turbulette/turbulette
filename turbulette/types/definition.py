from typing import Dict, Union
from starlette.config import Config


DatabaseSettings = Dict[str, Union[Config, str]]
