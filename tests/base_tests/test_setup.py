import pytest
from ariadne.asgi import GraphQL
from starlette.applications import Starlette

from turbulette import setup as turbulette_setup
from turbulette import turbulette_starlette
from turbulette.conf.exceptions import ImproperlyConfigured


def test_minimal_setup(settings):
    schema = turbulette_setup(settings)
    assert isinstance(schema, GraphQL)


def test_missing_settings_module():
    with pytest.raises(ImproperlyConfigured):
        assert turbulette_setup()


@pytest.mark.usefixtures("reload_resources")
def test_starlette_setup(settings):
    app = turbulette_starlette(settings)
    assert isinstance(app, Starlette)
