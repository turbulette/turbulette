"""Turbulette conf package."""

from gino_starlette import Gino
from simple_settings import LazySettings
from starlette.applications import Starlette

from turbulette.apps.registry import Registry
from turbulette.conf.constants import OVERRIDE_BY_ENV  # noqa
from turbulette.utils import LazyInitMixin

from . import constants
from .utils import get_config_from_paths  # noqa


class LazyRegistry(LazyInitMixin, Registry):
    """Lazy init the Turbulette registry."""

    def __init__(self):
        super().__init__("Registry")


class LazyStarlette(LazyInitMixin, Starlette):
    """Lazy init the Starlette instance."""

    def __init__(self):
        super().__init__("Starlette app")


class LazyGino(LazyInitMixin, Gino):
    """Lazy init the GINO instance."""

    def __init__(self):
        super().__init__("GINO")


registry: LazyRegistry = LazyRegistry()
"""`LazyRegistry` instance.

Holds all Turbulette apps in use.
"""

db: LazyGino = LazyGino()
"""`LazyGino` instance.

This is the main access point to interact with the database.
"""

settings: LazySettings = None
"""`LazySettings` instance.

Contains the parameters defined in each one (default values)
and the project parameters (can replace them).

!!! info
    The application parameters are loaded first, as they define the default values.
    The project parameters come last, so they can override the default settings of the applications.
"""

app: LazyStarlette = LazyStarlette()
"""`LazyStarlette` instance."""


SIMPLE_SETTINGS = {
    constants.REQUIRED_SETTINGS: set(),
    constants.REQUIRED_SETTINGS_TYPES: {},
    constants.REQUIRED_NOT_NONE_SETTINGS: set(),
    constants.SETTINGS_LOGS: False,
    constants.OVERRIDE_BY_ENV: True,
}
