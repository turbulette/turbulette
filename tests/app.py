"""API entrypoint."""

from os import environ

from turbulette import turbulette
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE

environ.setdefault(PROJECT_SETTINGS_MODULE, "tests.settings")
app = turbulette()
