from importlib import reload
from os import environ

import pytest
from ariadne.asgi import GraphQL
from starlette.applications import Starlette

from turbulette import setup as turbulette_setup
from turbulette import get_app
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.conf.exceptions import ImproperlyConfigured


@pytest.mark.usefixtures("reload_resources")
def test_minimal_setup(settings_no_apps):
    schema = turbulette_setup(settings_no_apps)
    assert isinstance(schema, GraphQL)


@pytest.mark.usefixtures("reload_resources")
def test_settings_by_env():
    environ[PROJECT_SETTINGS_MODULE] = "tests.settings_no_apps"
    assert get_app()
    assert turbulette_setup()
    environ.pop(PROJECT_SETTINGS_MODULE)


@pytest.mark.usefixtures("reload_resources")
def test_missing_settings_module():
    with pytest.raises(ImproperlyConfigured):
        turbulette_setup()


@pytest.mark.usefixtures("reload_resources")
def test_wrong_env_file():
    with pytest.raises(ImproperlyConfigured):
        turbulette_setup("tests.settings_wrong_env")


@pytest.mark.usefixtures("reload_resources")
def test_starlette_setup(settings):
    app = get_app(settings)
    assert isinstance(app, Starlette)


@pytest.mark.asyncio
@pytest.mark.usefixtures("reload_resources")
async def test_lazy_init_mixin():
    from turbulette import cache
    from turbulette.exceptions import NotReady

    reload(cache)
    with pytest.raises(NotReady):
        await cache.cache.connect()


@pytest.mark.usefixtures("reload_resources")
def test_no_database(settings_no_apps_module, settings_no_apps):
    # Simulate removing `DB_HOST` from .env
    # settings_no_apps_module.DATABASES["DB_HOST"] = None
    # turbulette_setup(settings_no_apps)

    # Simulate removing `DATABASE_CONNECTION` from project settings
    delattr(settings_no_apps_module, "DATABASES")
    turbulette_setup(settings_no_apps)
