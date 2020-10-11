from os import environ
from turbulette import turbulette_starlette

environ.setdefault("TURBULETTE_SETTINGS_MODULE", "{{ settings }}")
app = turbulette_starlette()
