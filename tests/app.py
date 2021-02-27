"""API entrypoint."""

from os import environ

from turbulette import turbulette_starlette
from turbulette.asgi import GinoConnection
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE

environ.setdefault(PROJECT_SETTINGS_MODULE, "tests.settings")
app = turbulette_starlette(db_connection=GinoConnection)
