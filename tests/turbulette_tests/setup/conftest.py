from importlib import import_module, reload

import pytest

from turbulette.apps import Registry


@pytest.fixture(scope="session")
def settings():
    return "tests.settings"


@pytest.fixture(scope="session")
def settings_no_apps():
    return "tests.settings_no_apps"


@pytest.fixture
def settings_no_apps_module(settings_no_apps):
    return import_module(settings_no_apps)


@pytest.fixture
def auth_app_module_name():
    return "turbulette.apps.auth"


@pytest.fixture
def base_app_module_name():
    return "turbulette.apps.base"


@pytest.fixture
def reload_resources(settings, settings_no_apps, base_app_module_name):
    """Reload modules that may have been modified"""
    # Reload modules that may have been modified
    reload(import_module(settings))
    reload(import_module(settings_no_apps))
    reload(import_module("turbulette.conf"))
    reload(import_module(f"{base_app_module_name}.resolvers.root_types"))
    reload(import_module(base_app_module_name))
    reload(import_module("turbulette.apps.registry"))
    reload(import_module("turbulette.validation"))


@pytest.fixture
def registry(settings_no_apps):
    return Registry(settings_path=settings_no_apps)
