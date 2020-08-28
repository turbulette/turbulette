from typing import Optional

from gino_starlette import Gino
from simple_settings import LazySettings
from turbulette.conf.constants import OVERRIDE_BY_ENV
from turbulette.apps.registry import Registry

from . import constants
from .utils import get_config_from_paths

registry: Optional[Registry] = None
db: Gino = None
settings: LazySettings = None
app = None

SIMPLE_SETTINGS = {
    constants.REQUIRED_SETTINGS: set(),
    constants.REQUIRED_SETTINGS_TYPES: {},
    constants.REQUIRED_NOT_NONE_SETTINGS: set(),
    constants.SETTINGS_LOGS: False,
    constants.OVERRIDE_BY_ENV: True,
}
