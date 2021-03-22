"""API entry point."""

from os import environ

from turbulette import turbulette

environ.setdefault("TURBULETTE_SETTINGS_MODULE", "{{ settings }}")
app = turbulette()
