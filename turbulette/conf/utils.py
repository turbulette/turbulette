from importlib import import_module
from pathlib import Path
from typing import List, Type
from simple_settings.utils import SettingsStub
from starlette.config import Config

from .exceptions import ImproperlyConfigured


def get_config_from_paths(paths: List[str]) -> Config:
    """Return a Starlette `Config` instance from the first existing path.

    Args:
        paths (List[str]): Paths to config file to try

    Raises:
        ImproperlyConfigured: Raised if none of the given paths exists

    Returns:
        A `Config` instance
    """
    for path_str in paths:
        path = Path(path_str)
        if path.is_file():
            return Config(path.as_posix())
    raise ImproperlyConfigured(f"Failed to find config file from these paths : {paths}")


class TurubuletteSettingsStub(SettingsStub):
    """Subclass of SettingsStub to make it work with Turbulette settings.

    It's a simple context manager that can be used to safely
    change settings on the fly in tests:

    ```python
    async def test_something(tester):
        from turbulette.conf.utils import settings_stub
        with settings_stub(MY_SETTING="special_value"):
            # some tests
    ```
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Need to import here to make sure settings are initialized
        self.settings = getattr(import_module("turbulette.conf"), "settings")
        self.old_settings = None

    def __enter__(self):
        """Replace the corresponding Turbulette settings."""
        self.settings.setup()
        self.old_settings = self.settings.as_dict()
        self.settings.configure(**self.new_settings)

    def __exit__(self, ext_type, exc_value, traceback):
        """Restore old settings."""
        self.settings.configure(**self.old_settings)


settings_stub: Type[TurubuletteSettingsStub] = TurubuletteSettingsStub
