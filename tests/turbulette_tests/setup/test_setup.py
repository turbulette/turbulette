from importlib import reload
from os import environ

import pytest
from ariadne.asgi import GraphQL
from starlette.applications import Starlette

from turbulette import setup as turbulette_setup
from turbulette import turbulette_starlette
from turbulette.conf.constants import ENV_TURBULETTE_SETTINGS
from turbulette.conf.exceptions import ImproperlyConfigured


def test_minimal_setup(settings_no_apps):
    schema = turbulette_setup(settings_no_apps)
    assert isinstance(schema, GraphQL)


def test_settings_by_env():
    environ[ENV_TURBULETTE_SETTINGS] = "tests.settings_no_apps"
    assert turbulette_setup()
    environ.pop(ENV_TURBULETTE_SETTINGS)


def test_missing_settings_module():
    with pytest.raises(ImproperlyConfigured):
        turbulette_setup()


def test_wrong_env_file():
    with pytest.raises(ImproperlyConfigured):
        turbulette_setup("tests.settings_wrong_env")


@pytest.mark.usefixtures("reload_resources")
def test_starlette_setup(settings):
    app = turbulette_starlette(settings)
    assert isinstance(app, Starlette)


@pytest.mark.asyncio
async def test_lazy_init_mixin():
    from turbulette.core import cache
    from turbulette.core.exceptions import NotReady

    reload(cache)
    with pytest.raises(NotReady):
        await cache.cache.connect()


@pytest.mark.usefixtures("reload_resources")
def test_no_database(settings_no_apps_module, settings_no_apps):
    # Simulate removing `DB_HOST` from .env
    settings_no_apps_module.DATABASE_CONNECTION["DB_HOST"] = None
    turbulette_setup(settings_no_apps)

    # Simulate removing `DATABASE_CONNECTION` from project settings
    delattr(settings_no_apps_module, "DATABASE_CONNECTION")
    turbulette_setup(settings_no_apps)
