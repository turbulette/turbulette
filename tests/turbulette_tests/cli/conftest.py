import contextlib
import sys
from datetime import datetime
from importlib import import_module
from os import chdir, environ
from pathlib import Path
from tempfile import TemporaryDirectory
from gino_backend import GinoBackend

import pytest
from click.testing import CliRunner
from gino_starlette import Gino

from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.management.cli import cli

PROJECT = "__test_project"
APP_1 = "__test_app_1"
APP_2 = "__test_app_2"
APP_3 = "__test_app_3"

_USER_MODEL = """
from turbulette.apps.auth.models import AbstractUser
from gino_backend.model import Model

class User(AbstractUser, Model):
    pass
"""


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
        assert res.exit_code == 0
    environ[PROJECT_SETTINGS_MODULE] = f"{PROJECT}.settings"
    yield Path(tmp_dir.name) / PROJECT
    environ.pop(PROJECT_SETTINGS_MODULE)
    tmp_dir.cleanup()


@pytest.fixture(scope="session")
def create_apps(create_project):
    runner = CliRunner()
    with working_directory(create_project):
        res = runner.invoke(
            cli, ["app", "--name", APP_1, "--name", APP_2, "--name", APP_3]
        )
        assert res.exit_code == 0


@pytest.fixture(scope="session")
def auth_app(create_project, create_apps):
    # AUTH_USER_MODEL setting
    settings_file = (create_project / "settings.py").read_text()
    auth_user_model = (
        settings_file + f"\nAUTH_USER_MODEL='{PROJECT}.{APP_1}.models.User'"
    )

    # Add a blank user model subclassing `AbstractUser`
    (create_project / "settings.py").write_text(auth_user_model)
    (create_project / APP_1 / "models.py").write_text(_USER_MODEL)

    # Add auth to INSTALLED_APPS
    env_file = (create_project / ".env").read_text()
    add_auth_app = env_file.replace(
        "INSTALLED_APPS=", f"INSTALLED_APPS=turbulette.apps.auth,{PROJECT}.{APP_1}"
    )
    (create_project / ".env").write_text(add_auth_app)

    yield APP_1

    # Restore initial settings
    (create_project / "settings.py").write_text(settings_file)
    (create_project / APP_1 / "models.py").write_text("")
    (create_project / ".env").write_text(env_file)


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
    db = Gino()

    # Connect to the default "template1" database to create a new one
    url = GinoBackend.make_url(
        getattr(project_settings_cli, "DATABASES")["connection"], database="template1"
    )

    async with db.with_bind(str(url), min_size=1, max_size=2) as engine:
        async with engine.acquire():
            await engine.status(f'CREATE DATABASE "{db_name_cli}"')
            project_settings_cli.DATABASES["connection"]["DB_DATABASE"] = db_name_cli
            yield
            # Drop the test db if needed
            if not request.config.getoption("--keep-db", default=False):
                await engine.status(f'DROP DATABASE "{db_name_cli}"')
