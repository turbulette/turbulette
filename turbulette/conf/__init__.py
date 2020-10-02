"""Turbulette conf package.

Holds the following global resources :

    - db: the GINO instance
    - registry: Turbulette registry
    - settings: Turbulette settings
    - app: The Starlette application
"""

from gino_starlette import Gino
from simple_settings import LazySettings
from starlette.applications import Starlette

from turbulette.apps.registry import Registry
from turbulette.conf.constants import OVERRIDE_BY_ENV  # noqa
from turbulette.utils import LazyInitMixin

from . import constants
from .utils import get_config_from_paths  # noqa


class LazyRegistry(LazyInitMixin, Registry):
    def __init__(self):
        super().__init__("Registry")


class LazyStarlette(LazyInitMixin, Starlette):
    def __init__(self):
        super().__init__("Starlette app")


class LazyGino(LazyInitMixin, Gino):
    def __init__(self):
        super().__init__("GINO")


registry = LazyRegistry()
db = LazyGino()
settings: LazySettings = None
app = LazyStarlette()


SIMPLE_SETTINGS = {
    constants.REQUIRED_SETTINGS: set(),
    constants.REQUIRED_SETTINGS_TYPES: {},
    constants.REQUIRED_NOT_NONE_SETTINGS: set(),
    constants.SETTINGS_LOGS: False,
    constants.OVERRIDE_BY_ENV: True,
}
