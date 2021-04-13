from turbulette.utils import LazyInitMixin
from typing import Any
from types import ModuleType

from turbulette.conf.constants import SETTINGS_DATABASE_SETTINGS, SETTINGS_DB_DSN
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.types import DatabaseConnectionParams, DatabaseSettings


class DatabaseBackend:
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
        db.__setup__(self.database)
        db_backend.__setup__(self)
        return self.database

    def create_db(self) -> Any:
        raise NotImplementedError()


    def startup(self):
        pass

    def shutdown(self):
        pass

    @classmethod
    def create_test_db(
        cls,
        project_settings: ModuleType,
        db_name: str,
        keep: bool,
        **kwargs
    ) -> Any:
        raise NotImplementedError()


class LazyDatabase(LazyInitMixin):
    """Lazy init the GINO instance."""

    def __init__(self):
        super().__init__("Database")


db: LazyDatabase = LazyDatabase()
"""`LazyGino` instance.

This is the main access point to interact with the database.
"""

class LazyBackend(LazyInitMixin, DatabaseBackend):
    """Lazy init the GINO instance."""

    def __init__(self):
        super().__init__("Backend")

db_backend: LazyBackend = LazyBackend()
"""`LazyBackend` instance.
"""
