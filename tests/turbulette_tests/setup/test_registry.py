from os import environ

import pytest
from simple_settings import LazySettings

from turbulette.apps import TurbuletteApp
from turbulette.apps.exceptions import RegistryError
from turbulette.apps.registry import Registry
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.conf.exceptions import ImproperlyConfigured


def test_init():
    environ.pop(PROJECT_SETTINGS_MODULE, None)
    with pytest.raises(ImproperlyConfigured):
        Registry()


@pytest.mark.usefixtures("reload_resources")
def test_setup(settings_no_apps):
    registry = Registry(project_settings=settings_no_apps)
    registry.setup()


@pytest.mark.usefixtures("reload_resources")
def test_setup_no_schema(registry):
    registry.apps = {}
    with pytest.raises(RegistryError):
        registry.setup()


@pytest.mark.usefixtures("reload_resources")
def test_register_app(settings_no_apps, registry):
    nb_app = len(registry.apps)
    app = TurbuletteApp("turbulette.apps.auth")
    registry.register(app)
    assert len(registry.apps) == nb_app + 1
    with pytest.raises(RegistryError):
        registry.register(app)


@pytest.mark.usefixtures("reload_resources")
def test_federation(registry, settings_no_apps_module):
    settings_no_apps_module.APOLLO_FEDERATION = True
    registry.setup()


@pytest.mark.usefixtures("reload_resources")
def test_load_resources(registry):
    settings_1 = registry.load_settings()
    assert isinstance(settings_1, LazySettings)
    settings_2 = registry.load_settings()
    assert isinstance(settings_2, LazySettings)
    assert settings_1 is settings_2
    registry.load_models()


@pytest.mark.usefixtures("reload_resources")
def test_ready(registry):
    assert registry.ready == False
    registry.setup()
    assert registry.ready == True
    # Second return
    assert registry.ready == True
    with pytest.raises(ValueError):
        registry.ready = False


@pytest.mark.usefixtures("reload_resources")
def test_get_app_by_label(registry):
    assert registry.get_app_by_label("base").label == "base"
    with pytest.raises(RegistryError):
        registry.get_app_by_label("unkown_app")


@pytest.mark.usefixtures("reload_resources")
def test_get_app_by_package(registry):
    assert registry.get_app_by_package("turbulette.apps.base").label == "base"
    with pytest.raises(RegistryError):
        registry.get_app_by_package("unkown_app")
