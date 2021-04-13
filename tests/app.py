"""API entrypoint."""

from os import environ

from turbulette import get_app
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE

environ.setdefault(PROJECT_SETTINGS_MODULE, "tests.settings")
app = get_app()
