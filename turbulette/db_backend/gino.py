from importlib.util import find_spec
from pathlib import Path
from turbulette.test.pytest_plugin import db_name
from typing import Any

from gino_starlette import Gino  # type: ignore [attr-defined]
from sqlalchemy.engine.url import URL
from starlette.applications import Starlette
from turbulette.db_backend.core import DatabaseConnection
from turbulette import conf
from alembic.config import Config
from alembic.command import upgrade
from turbulette.type import DatabaseConnectionParams
from gino import create_engine  # type: ignore


class GinoConnection(DatabaseConnection):
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

    @classmethod
    def on_startup(cls, app: Starlette) -> None:
        conf.db.init_app(app)

    @classmethod
    def create_test_db(cls, conn_params: DatabaseConnectionParams, project_settings):
        return _CreateTestDatabase(conn_params, project_settings)


class _CreateTestDatabase:
    def __init__(
        self,
        conn_params: DatabaseConnectionParams,
        project_settings,
        db_name: str,
        keep: bool,
    ) -> None:
        self.conn_params = conn_params
        self.project_settings = project_settings
        self.db_name = db_name
        self.keep = keep

    async def __aenter__(self):
        url = URL(
            drivername=self.conn_params["DB_DRIVER"],
            username=self.conn_params["DB_USER"],
            password=self.conn_params["DB_PASSWORD"],
            host=self.conn_params["DB_HOST"],
            port=self.conn_params["DB_PORT"],
            database="template1",
        )
        # Connect to the default template1 database to create a new one
        # project_settings.DB_DSN.database = "template1"
        # The pool must be able to authorize two connection to drop the test db if needed
        self.engine_1 = await create_engine(str(url), min_size=1, max_size=2)
        self.engine_1.acquire()
        await self.engine_1.status(f'CREATE DATABASE "{db_name}"')
        url.database = db_name
        self.engin_2 = await conf.db.set_bind(bind=url)
        settings_file = Path(find_spec(self.project_settings.__name__).origin)
        alembic_config = (settings_file.parent / "alembic.ini").as_posix()
        script_location = (settings_file.parent / "alembic").as_posix()

        config = Config(file_=alembic_config)
        config.set_main_option("sqlalchemy.url", str(url))
        config.set_main_option("script_location", script_location)
        upgrade(config, "heads")

    async def __aexit__(self):
        self.engine_2.pop_bind().close()
        if not self.keep:
            await self.engine_1.status(f'DROP DATABASE "{self.db_name}"')
