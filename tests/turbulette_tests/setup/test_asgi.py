from importlib import import_module, reload

import pytest

from turbulette import get_app
from turbulette.conf.exceptions import ImproperlyConfigured


@pytest.mark.usefixtures("reload_resources")
def test_missing_db_settings(settings):
    settings_module = import_module(settings)
    settings_module.DATABASES["settings"] = None
    with pytest.raises(ImproperlyConfigured):
        get_app(settings)
    reload(settings_module)
    settings_module.DATABASES["settings"] = {"useless_key": "useless"}
    with pytest.raises(ImproperlyConfigured):
        get_app(settings)
    reload(settings_module)
    settings_module.DATABASES["connection"] = {}
    with pytest.raises(ImproperlyConfigured):
        get_app(settings)
    reload(settings_module)
