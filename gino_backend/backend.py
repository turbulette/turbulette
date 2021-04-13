from importlib.util import find_spec
from pathlib import Path
from types import ModuleType
from typing import Any

from alembic.command import upgrade
from alembic.config import Config
from gino import create_engine  # type: ignore
from gino_starlette import Gino  # type: ignore [attr-defined]
from sqlalchemy.engine.url import URL
from starlette.applications import Starlette

from turbulette.conf import app
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.db_backend import DatabaseBackend, db
from turbulette.types import DatabaseConnectionParams


class GinoBackend(DatabaseBackend):
    def create_db(self) -> Any:
        """Setup db connection using `gino_starlette` extension.

        Returns:
            The GINO instance
        """
        return Gino(
            dsn=URL(
                drivername=self.conn_params["DB_DRIVER"],
                username=self.conn_params["DB_USER"],
                password=self.conn_params["DB_PASSWORD"],
                host=self.conn_params["DB_HOST"],
                port=self.conn_params["DB_PORT"],
                database=self.conn_params["DB_DATABASE"],
            ),
            pool_min_size=self.settings["DB_POOL_MIN_SIZE"],
            pool_max_size=self.settings["DB_POOL_MAX_SIZE"],
            echo=self.settings["DB_ECHO"],
            ssl=self.settings["DB_SSL"],
            use_connection_for_request=self.settings["DB_USE_CONNECTION_FOR_REQUEST"],
            retry_limit=self.settings["DB_RETRY_LIMIT"],
            retry_interval=self.settings["DB_RETRY_INTERVAL"],
        )

    def startup(self) -> None:
        db.init_app(app)

    def create_test_db(
        self,
        project_settings: ModuleType,
        db_name: str,
        keep: bool,
    ) -> Any:
        return _CreateTestDatabase(
            project_settings,
            db_name,
            keep,
            url=self.make_url(self.conn_params, database="template1"),
        )

    @staticmethod
    def make_url(conn_params: DatabaseConnectionParams, **kwargs) -> URL:
        try:
            return URL(
                drivername=kwargs.get("drivername") or conn_params["DB_DRIVER"],
                username=kwargs.get("username") or conn_params["DB_USER"],
                password=kwargs.get("password") or conn_params["DB_PASSWORD"],
                host=kwargs.get("host") or conn_params["DB_HOST"],
                port=kwargs.get("port") or conn_params["DB_PORT"],
                database=kwargs.get("database") or conn_params["DB_DATABASE"],
            )
        except KeyError as error:
            raise ImproperlyConfigured(
                f"You did not set {error.args[0]} in database connection settings"
            )


class _CreateTestDatabase:
    def __init__(
        self,
        project_settings,
        db_name: str,
        keep: bool,
        **kwargs,
    ) -> None:
        self.url = kwargs["url"]
        self.project_settings = project_settings
        self.db_name = db_name
        self.keep = keep

    async def __aenter__(self):
        self.engine_1 = await create_engine(str(self.url), min_size=1, max_size=1)

        # Connect to the default "template1" database to create a new one
        async with self.engine_1.acquire():
            await self.engine_1.status(f'CREATE DATABASE "{self.db_name}"')

        self.url.database = self.db_name
        self.project_settings.DATABASES["connection"]["DB_DATABASE"] = self.db_name
        db.__setup__(Gino())
        self.engine_2 = await db.set_bind(bind=self.url)

        settings_file = Path(find_spec(self.project_settings.__name__).origin)
        alembic_config = (settings_file.parent / "alembic.ini").as_posix()
        script_location = (settings_file.parent / "alembic").as_posix()

        config = Config(file_=alembic_config)
        config.set_main_option("sqlalchemy.url", str(self.url))
        config.set_main_option("script_location", script_location)
        upgrade(config, "heads")

    async def __aexit__(self, *_):
        await self.engine_2.close()
        if not self.keep:
            async with self.engine_1.acquire():
                await self.engine_1.status(f'DROP DATABASE "{self.db_name}"')
        await self.engine_1.close()
