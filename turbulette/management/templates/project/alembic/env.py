from os import environ
from turbulette.management.alembic_env import run_migrations

environ.setdefault("TURBULETTE_SETTINGS_MODULE", "settings")
run_migrations()
