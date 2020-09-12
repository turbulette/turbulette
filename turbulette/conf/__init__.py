"""Turbulette conf package.

Holds the following global resources :

    - db: the GINO instance
    - registry: Turbulette registry
    - settings: Turbulette settings
    - app: The Starlette application
"""

from typing import Optional

from gino_starlette import Gino
from simple_settings import LazySettings
from starlette.applications import Starlette
from turbulette.apps.registry import Registry
from turbulette.conf.constants import OVERRIDE_BY_ENV  # noqa
from turbulette.apps.exceptions import RegistryError

from . import constants
from .utils import get_config_from_paths  # noqa

registry: Optional[Registry] = None
db: Gino = None
settings: LazySettings = None
app: Optional[Starlette] = None

SIMPLE_SETTINGS = {
    constants.REQUIRED_SETTINGS: set(),
    constants.REQUIRED_SETTINGS_TYPES: {},
    constants.REQUIRED_NOT_NONE_SETTINGS: set(),
    constants.SETTINGS_LOGS: False,
    constants.OVERRIDE_BY_ENV: True,
}


def reg() -> Registry:
    """An access point to get a `Registry` type instead of an `Optional[Registry]`.

    The conf module provide the `registry` attribute, but it's initialized to `None`,
    so it may not be the safest way to manipulate it. This ensure that the registry is
    initialized (i.e : is not None), and will raise an exception if not.

    This should be the preferred way to access the registry.

    Raises:
        RegistryError: Raised if the registry is not ready

    Returns:
        Registry: A registry ready to be used
    """
    # This is a bit dirty, the proper way would be to replace this function by overriding
    # `__gettatr__` on module level to control the `registry` module attribute access.
    # But it's a Python 3.7+ feature and we want 3.6 compatibility
    if registry is None:
        raise RegistryError("The registry is not ready yet")
    return registry
