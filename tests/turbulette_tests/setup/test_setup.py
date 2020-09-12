from os import environ
import pytest
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from turbulette import setup as turbulette_setup
from turbulette import turbulette_starlette
from turbulette.apps import Registry
from turbulette.apps.exceptions import RegistryError
from turbulette.conf.constants import ENV_TURBULETTE_SETTINGS
from turbulette.conf.exceptions import ImproperlyConfigured


def test_minimal_setup(settings):
    schema = turbulette_setup(settings)
    assert isinstance(schema, GraphQL)


def test_settings_by_env():
    environ[ENV_TURBULETTE_SETTINGS] = "tests.settings"
    assert turbulette_setup()
    environ.pop(ENV_TURBULETTE_SETTINGS)


def test_missing_settings_module():
    with pytest.raises(ImproperlyConfigured):
        assert turbulette_setup()


def test_wrong_env_file():
    with pytest.raises(ImproperlyConfigured):
        assert turbulette_setup("tests.settings_wrong_env")


@pytest.mark.usefixtures("reload_resources")
def test_starlette_setup(settings):
    app = turbulette_starlette(settings)
    assert isinstance(app, Starlette)


@pytest.mark.usefixtures("reload_resources")
def test_reg(settings):
    from turbulette.conf import reg

    turbulette_setup(settings)
    registry = reg()
    assert isinstance(registry, Registry)


@pytest.mark.usefixtures("reload_resources")
def test_reg_not_initialized():
    from turbulette.conf import reg

    with pytest.raises(RegistryError):
        reg()
