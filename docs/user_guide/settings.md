Any Turbulette project created using the `turb` CLI comes with a default settings module with minimal settings to get a working hello world.

Settings management is another Django-inspired concept, but Turbulette extends it a bit by allowing applications to have their own `settings` module.
This avoid rewriting a settings registry when writing an application, and is an easy way to define default values.

The project settings module is always loaded last on startup, so default values can be set by applications (in their own settings module) and overridden in project settings.

## Load settings from .env file

Following [twelve-factor methodology](https://12factor.net) , Turbulette strongly encourages strict separation between code and settings because config is likely to vary between deployments, code does *not*.

 To help you, Starlette provides a `Config` object that reads settings from environment variables and/or `.env` files:

```python
# settings.py

from starlette.config import Config

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

DEBUG = config('DEBUG', cast=bool, default=False)
```

See Starlette's [Config docs](https://www.starlette.io/config/) for more details.

### Try different paths

Turbulette has a small helper to try different paths when loading `.env` files:

```python
# settings.py

from turbulette.conf import get_config_from_paths

config = get_config_from_paths(["project/.env", "../project/.env"])
```

`get_config_from_paths` will try all paths in order, stop on the first existing one and return a `Config` instance with it.

In the above example, you can start your server in the root folder (containing the the Turbulette project folder), *or* inside the project folder (in this case, the second path will be be picked).
