from importlib import import_module, reload

import pytest

from turbulette.apps import Registry


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
def registry(settings_no_apps):
    return Registry(settings_path=settings_no_apps)
