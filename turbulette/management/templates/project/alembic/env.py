"""Alembic script."""

from os import environ

from gino_backend.alembic_env import run_migrations

environ.setdefault("TURBULETTE_SETTINGS_MODULE", "settings")
run_migrations()
