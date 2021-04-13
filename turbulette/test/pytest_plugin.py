"""Turbulette's pytest plugin."""

import asyncio
from datetime import datetime
from importlib import import_module, reload

from os import environ
from pathlib import Path

import pytest
from starlette.config import Config as starlette_config

from turbulette import conf, db_backend, setup
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.test.tester import Tester
from turbulette.utils import import_class


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
        if PROJECT_SETTINGS_MODULE in environ:
            res = environ[PROJECT_SETTINGS_MODULE]
        else:
            if Path(Path.cwd() / ".env").is_file():
                env = Path(Path.cwd() / ".env")
            else:
                raise ImproperlyConfigured("Cannot find the .env file")
            config = starlette_config(env)
            res = config.get(PROJECT_SETTINGS_MODULE)
            # Needed to make it available for alembic in env.py
            environ[PROJECT_SETTINGS_MODULE] = res
    return import_module(res)


# Redefine event_loop to have a broader scope
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_name():
    """Return the name of the test database.

    Scope: `session`

    The name is generated as follows : `test_YYY-MM-DDThh:mm:ss`
    """
    return f"test_{datetime.now().replace(microsecond=0).isoformat()}"


@pytest.fixture(scope="session")
async def turbulette_setup(project_settings, request, db_name):
    """Create a test database, apply alembic revisions and setup turbulette project.

    Scope: `session`

    Depends on : [create_db][turbulette.test.pytest_plugin.create_db]
    """
    conf_module = reload(import_module("turbulette.conf"))
    db_backend = import_class(project_settings.DATABASES["backend"])(
        settings=project_settings.DATABASES["settings"],
        conn_params=project_settings.DATABASES["connection"],
    )
    keep_db = request.config.getoption("--keep-db", default=False)

    async with db_backend.create_test_db(project_settings, db_name, keep_db):
        setup(project_settings.__name__)
        cache = getattr(import_module("turbulette.cache"), "cache")
        await cache.connect()
        yield conf_module
        if cache.is_connected:
            await cache.disconnect()


@pytest.fixture(scope="session")
def tester(turbulette_setup):
    """Session fixture that return a [Tester][turbulette.test.tester.Tester] instance.

    Scope: `session`

    Depends on : [turbulette_setup][turbulette.test.pytest_plugin.turbulette_setup]
    """
    return Tester(turbulette_setup.registry.schema)


@pytest.fixture
def blank_conf():
    """Reload the conf package to clear `db`, `registry` and `settings`.

    Scope: `function`
    """
    app, registry, db, settings = conf.app, conf.registry, db_backend.db, conf.settings
    reload(conf)
    reload(db_backend)
    yield
    conf.app, db_name.db, conf.registry, conf.settings = app, db, registry, settings
