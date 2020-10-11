from os import environ

from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.management.alembic_env import run_migrations

environ.setdefault(PROJECT_SETTINGS_MODULE, "tests.settings")
run_migrations()
