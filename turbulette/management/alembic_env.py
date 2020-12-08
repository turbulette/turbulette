import sys
from importlib import import_module
from logging.config import fileConfig
from pathlib import Path
from typing import Optional
from turbulette.utils import get_project_settings
from alembic import context
from sqlalchemy import engine_from_config, pool
from turbulette.apps import Registry
from turbulette.main import get_gino_instance
from turbulette import conf


def _run_migrations_offline(metadata, config):  # pragma: no cover
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _run_migrations_online(metadata, config):  # pragma: no cover
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)

        with context.begin_transaction():
            context.run_migrations()


def run_migrations(project_settings: Optional[str] = None):
    """Apply migrations for installed apps depending on the context (online/offline)."""
    # Add project folder to python path
    sys.path[0:0] = [str(Path.cwd().parent.resolve()), str(Path.cwd().resolve())]

    settings = import_module(get_project_settings(project_settings))

    registry = Registry(project_settings_module=settings)
    if not conf.registry.__initialized__:
        conf.registry.__setup__(registry)
    registry.load_settings()

    database = get_gino_instance()

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    alembic_config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    fileConfig(alembic_config.config_file_name)

    # add your model's MetaData object here
    # for 'autogenerate' support
    metadata = database
    registry.load_models()
    alembic_config.set_main_option("sqlalchemy.url", str(settings.DB_DSN))  # type: ignore

    if context.is_offline_mode():  # pragma: no cover
        _run_migrations_offline(metadata, alembic_config)
    else:
        _run_migrations_online(metadata, alembic_config)
