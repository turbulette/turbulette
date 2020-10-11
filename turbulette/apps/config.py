from importlib import import_module
from os import environ
from types import ModuleType

from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE


def get_project_settings_by_env() -> ModuleType:
    """Try to find turbulette settings in env vars.

    Raises:
        ImproperlyConfigured: Raised if `TURBULETTE_SETTINGS` env var was not found

    Returns:
        ModuleType: The settings module
    """
    if PROJECT_SETTINGS_MODULE not in environ:
        raise ImproperlyConfigured(
            "You must provide project settings either by passing the module name in args"
            + " to turbulette() or by setting the TURBULETTE_SETTINGS environment variable"
        )
    return import_module(environ[PROJECT_SETTINGS_MODULE])
