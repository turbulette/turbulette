from turbulette.type import DatabaseSettings, DatabaseConnectionParams
from starlette.applications import Starlette
from typing import Any
from turbulette import conf
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.conf.constants import SETTINGS_DATABASE_SETTINGS, SETTINGS_DB_DSN


class DatabaseConnection:
    """Manage connection to a data source."""

    def __init__(
        self, settings: DatabaseSettings, conn_params: DatabaseConnectionParams
    ) -> None:
        self.settings = settings
        self.conn_params = conn_params
        self.database = None

    def connect(self) -> Any:
        """
        Create the database instance by calling the specific method.

        Raises:
            ImproperlyConfigured: Raised if either `settings` or `dsn`
                                are incorrect or have missing values
        """
        if not self.settings:
            raise ImproperlyConfigured(
                f"You did not set the {SETTINGS_DATABASE_SETTINGS} setting"
            )
        if not self.conn_params:
            raise ImproperlyConfigured(f"You did not set the {SETTINGS_DB_DSN} setting")
        try:
            self.database = self.create_db()
        except KeyError as error:
            raise ImproperlyConfigured(
                f"You did not set {error.args[0]} in {SETTINGS_DATABASE_SETTINGS}"
            ) from error
        conf.db.__setup__(self.database)
        return self.database

    def create_db(self) -> Any:
        raise NotImplementedError()

    def on_startup(self, app: Starlette) -> None:
        pass
