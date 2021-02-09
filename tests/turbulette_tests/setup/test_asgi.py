from importlib import import_module, reload

import pytest

from turbulette import turbulette_starlette
from turbulette.conf.exceptions import ImproperlyConfigured


@pytest.mark.usefixtures("reload_resources")
def test_missing_db_settings(settings):
    settings_module = import_module(settings)
    settings_module.DATABASE_SETTINGS = None
    with pytest.raises(ImproperlyConfigured):
        turbulette_starlette(settings)
    reload(settings_module)
    settings_module.DATABASE_SETTINGS = {"useless_key": "useless"}
    with pytest.raises(ImproperlyConfigured):
        turbulette_starlette(settings)
    reload(settings_module)
    settings_module.DB_DSN = {}
    with pytest.raises(ImproperlyConfigured):
        turbulette_starlette(settings)
    reload(settings_module)
