import asyncio
from datetime import datetime
from importlib import import_module, reload
from importlib.util import find_spec
from os import environ
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from gino import Gino, create_engine
from starlette.config import Config as starlette_config

from turbulette import conf, setup
from turbulette.conf.constants import PYTEST_TURBULETTE_SETTINGS
from turbulette.conf.exceptions import ImproperlyConfigured

from .tester import Tester


def pytest_addoption(parser):
    parser.addoption("--settings", action="store", help="Turbulette settings")
    parser.addoption(
        "--keep-db",
        action="store_true",
        help="Keep test database after the test session",
    )


@pytest.fixture(scope="session")
def project_settings(request):
    res = request.config.getoption("--settings", default=None)
    if not res:
        if PYTEST_TURBULETTE_SETTINGS in environ:
            res = environ[PYTEST_TURBULETTE_SETTINGS]
        else:
            if Path(Path.cwd() / ".env").is_file():
                env = Path(Path.cwd() / ".env").as_posix()
            else:
                raise ImproperlyConfigured("Cannot find the .env file")
            config = starlette_config(env)
            res = config.get(PYTEST_TURBULETTE_SETTINGS)
            # Needed to make it available for alembic in env.py
            environ[PYTEST_TURBULETTE_SETTINGS] = res
    return import_module(res)


# Redefine event_loop to have a broader scope
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_name():
    return f"test_{datetime.now().replace(microsecond=0).isoformat()}"


@pytest.fixture(scope="session")
async def turbulette_setup(project_settings, create_db):
    conf_module = reload(import_module("turbulette.conf"))
    setup(project_settings.__name__, database=True)
    async with conf.db.with_bind(bind=project_settings.DB_DSN) as engine:
        settings_file = Path(find_spec(project_settings.__name__).origin)
        alembic_config = (settings_file.parent / "alembic.ini").as_posix()
        script_location = (settings_file.parent / "alembic").as_posix()

        config = Config(file_=alembic_config)
        config.set_main_option("sqlalchemy.url", str(project_settings.DB_DSN))
        config.set_main_option("script_location", script_location)
        upgrade(config, "heads")
        cache = getattr(import_module("turbulette.cache"), "cache")
        await cache.connect()
        yield conf_module
        if cache.is_connected:
            await cache.disconnect()
    await engine.close()


@pytest.fixture(scope="session")
async def create_db(db_name, project_settings, request):
    # Connect to the default template1 database to create a new one
    project_settings.DB_DSN.database = "template1"
    # The pool must be able to authorize two connection to drop the test db if needed
    engine = await create_engine(str(project_settings.DB_DSN), min_size=1, max_size=2)
    async with engine.acquire():
        await engine.status(f'CREATE DATABASE "{db_name}"')
        project_settings.DB_DSN.database = db_name
        yield
        # Drop the test db if needed
        if not request.config.getoption("--keep-db", default=False):
            await engine.status(f'DROP DATABASE "{db_name}"')
    await engine.close()


@pytest.fixture(scope="session")
def tester(turbulette_setup):
    return Tester(turbulette_setup.registry.schema)


@pytest.fixture
def blank_conf():
    app, registry, db, settings = conf.app, conf.registry, conf.db, conf.settings
    reload(conf)
    yield
    conf.app, conf.db, conf.registry, conf.settings = app, db, registry, settings
