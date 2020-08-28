from datetime import datetime
from importlib import import_module
from pathlib import Path
from shutil import rmtree

import pytest
from gino import create_engine

PROJECT = "__test_project"
APP_1 = "__test_app_1"
APP_2 = "__test_app_2"


def pytest_sessionfinish(session, exitstatus):
    project_dir = Path.cwd() / PROJECT
    if project_dir.is_dir():
        rmtree(project_dir.as_posix())


@pytest.fixture(scope="session")
def db_name_cli():
    return f"test_cli_{datetime.now().replace(microsecond=0).isoformat()}"


@pytest.fixture(scope="session")
def project_settings_cli():
    return import_module(f"{PROJECT}.settings")


@pytest.fixture(scope="session")
def create_env(db_name_cli):
    env_file = (Path.cwd() / PROJECT / ".env").open("w")
    env_file.writelines([
        "DB_DRIVER=postgresql"
        "DB_HOST=localhost"
        "DB_PORT=5432"
        "DB_USER=postgres"
        "DB_PASSWORD=\"\""
        f"DB_DATABASE={db_name_cli}"
    ])
    env_file.close()


@pytest.fixture(scope="session")
async def create_db_cli(db_name_cli, project_settings_cli, create_env, request):
    # Connect to the default template1 database to create a new one
    project_settings_cli.DB_DSN.database = "template1"
    # The pool must be able to authorize two connection to drop the test db if needed
    engine = await create_engine(str(project_settings_cli.DB_DSN), min_size=1, max_size=2)
    async with engine.acquire():
        await engine.status(f'CREATE DATABASE "{db_name_cli}"')
        project_settings_cli.DB_DSN.database = db_name_cli
        yield
        # Drop the test db if needed
        if not request.config.getoption("--keep-db", default=False):
            await engine.status(f'DROP DATABASE "{db_name_cli}"')
    await engine.close()
