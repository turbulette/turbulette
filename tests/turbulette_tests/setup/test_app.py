from importlib import import_module, reload

import pytest

from turbulette.apps import TurbuletteApp
from turbulette.apps.exceptions import TurbuletteAppError


def test_missing_module_path(base_app_module_name):
    base_app = import_module(base_app_module_name)
    base_app.__spec__.submodule_search_locations = []
    with pytest.raises(TurbuletteAppError):
        TurbuletteApp(base_app_module_name)
    reload(base_app)


@pytest.mark.usefixtures("reload_resources")
def test_repr(base_app_module_name):
    app = TurbuletteApp(base_app_module_name)
    assert repr(app) == f"<{TurbuletteApp.__name__}: {app.package_name}>"
