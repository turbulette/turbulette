"""API entry point."""

from os import environ

from turbulette import get_app

environ.setdefault("TURBULETTE_SETTINGS_MODULE", "{{ settings }}")
app = get_app()
