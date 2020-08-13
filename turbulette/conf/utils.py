from pathlib import Path
from typing import List

from starlette.config import Config

from .exceptions import ImproperlyConfigured


def get_config_from_paths(paths: List[str]) -> Config:
    """Return a Config instance from the first existing path

    Args:
        paths (List[str]): Paths to config file to try

    Raises:
        ImproperlyConfigured: Raised if none of the given paths exists

    Returns:
        Config: A Config instance
    """
    for path_str in paths:
        path = Path(path_str)
        if path.is_file():
            return Config(path.as_posix())
    raise ImproperlyConfigured(f"Failed to find config file from these paths : {paths}")
