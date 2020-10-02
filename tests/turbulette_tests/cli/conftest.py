from pathlib import Path
import contextlib
import sys
from datetime import datetime
from importlib import import_module
from os import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from click.testing import CliRunner
from gino import create_engine

from turbulette.management import cli as cli_mod
from turbulette.management.cli import cli

PROJECT = "__test_project"
APP_1 = "__test_app_1"
APP_2 = "__test_app_2"
APP_3 = "__test_app_3"


@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(prev_cwd)


@pytest.fixture(scope="session")
def create_project():
    tmp_dir = TemporaryDirectory()
    with working_directory(tmp_dir.name):
        runner = CliRunner()
        res = runner.invoke(cli, ["project", "--name", PROJECT])
        print(__file__)
        print(cli_mod.__file__)
        print(Path(cli_mod.__file__).parent / "templates" / "project")
        if (Path(cli_mod.__file__).parent / "templates" / "project").is_dir():
            print("it's a dir")
        else:
            print("nope")
        assert res.exit_code == 0
    yield Path(tmp_dir.name) / PROJECT
    tmp_dir.cleanup()


@pytest.fixture(scope="session")
def create_apps(create_project):
    runner = CliRunner()
    chdir(create_project)
    res = runner.invoke(cli, ["app", "--name", APP_1, "--name", APP_2, "--name", APP_3])
    assert res.exit_code == 0


@pytest.fixture(scope="session")
def db_name_cli():
    return f"test_cli_{datetime.now().replace(microsecond=0).isoformat()}"


@pytest.fixture(scope="session")
def project_settings_cli(create_env, create_project):
    sys.path.insert(1, create_project.parent.as_posix())
    with working_directory(create_project.parent.as_posix()):
        return import_module(f"{PROJECT}.settings")


@pytest.fixture(scope="session")
def create_env(db_name_cli, create_project):
    env_file = (create_project / ".env").read_text()
    env_file = env_file.replace("DB_DATABASE=", f"DB_DATABASE={db_name_cli}")
    env_file = env_file.replace("DB_HOST=", "DB_HOST=localhost")
    (create_project / ".env").write_text(env_file)


@pytest.fixture(scope="session")
async def create_db_cli(db_name_cli, project_settings_cli, request):
    # Connect to the default template1 database to create a new one
    project_settings_cli.DB_DSN.database = "template1"
    # The pool must be able to authorize two connection to drop the test db if needed
    engine = await create_engine(
        str(project_settings_cli.DB_DSN), min_size=1, max_size=2
    )
    async with engine.acquire():
        await engine.status(f'CREATE DATABASE "{db_name_cli}"')
        project_settings_cli.DB_DSN.database = db_name_cli
        yield
        # Drop the test db if needed
        if not request.config.getoption("--keep-db", default=False):
            await engine.status(f'DROP DATABASE "{db_name_cli}"')
    await engine.close()
