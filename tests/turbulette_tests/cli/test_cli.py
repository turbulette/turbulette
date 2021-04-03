from importlib import import_module, reload
from os import environ
from tempfile import TemporaryDirectory

from click.testing import CliRunner

import turbulette
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.management.cli import cli

from .conftest import APP_1, APP_2, APP_3, working_directory

import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()

def test_create_project():
    runner = CliRunner()
    with TemporaryDirectory() as tmp_dir:
        with working_directory(tmp_dir):
            res = runner.invoke(cli, ["project", "--name", "project_1"])
            assert res.exit_code == 0
            res = runner.invoke(
                cli,
                [
                    "project",
                    "--name",
                    "project_2",
                    "--app",
                    "app_1",
                    "--app",
                    "app_2",
                ],
            )
            assert res.exit_code == 0


def test_create_app(create_project):
    with working_directory(create_project):
        runner = CliRunner()
        res = runner.invoke(cli, ["app", "--name", "app_1"])
        assert res.exit_code == 0
        res = runner.invoke(cli, ["app", "--name", "app_2", "--name", "app_3"])
        assert res.exit_code == 0


def test_revision(create_project, create_db_cli, create_apps):
    with working_directory(create_project):
        cli_module = reload(turbulette.management.cli)
        runner = CliRunner()
        res = runner.invoke(cli_module.cli, ["initrevision", APP_1])
        assert res.exit_code == 0
        res = runner.invoke(cli_module.cli, ["initrevision", APP_2])
        res = runner.invoke(cli_module.cli, ["initrevision", APP_3])
        res = runner.invoke(cli_module.cli, ["makerevision", APP_1])
        res = runner.invoke(cli_module.cli, ["upgrade", APP_1])
        assert res.exit_code == 0
        # Should upgrade APP_2 and APP_3
        res = runner.invoke(cli_module.cli, ["upgrade"])
        assert res.exit_code == 0


def test_secret_key(create_project):
    with working_directory(create_project):
        runner = CliRunner()

        res = runner.invoke(cli, ["jwk", "--env"])
        assert res.exit_code == 0

        res = runner.invoke(cli, ["jwk", "--kty", "OKP", "--crv", "Ed25519"])
        assert res.exit_code == 0

        res = runner.invoke(cli, ["jwk", "--kty", "RSA", "--size", 2048, "--exp", 12])
        assert res.exit_code == 0

        # Missing size param
        res = runner.invoke(cli, ["jwk", "--kty", "RSA"])
        assert res.exit_code != 0

        # Wrong crv param
        res = runner.invoke(cli, ["jwk", "--kty", "EC", "--crv", "X448"])
        assert res.exit_code != 0


def test_create_user(create_project, create_db_cli, auth_app):
    # monkeypatch.setenv(TEST_MODE, "1")
    with working_directory(create_project):
        cli_module = reload(turbulette.management.cli)
        runner = CliRunner()

        # Update `INSTALLED_APPS` setting
        # reload(import_module(f"{create_project.name}.settings"))

        res = runner.invoke(cli_module.cli, ["initrevision", auth_app])
        assert res.exit_code == 0

        res = runner.invoke(cli_module.cli, ["upgrade"])
        assert res.exit_code == 0

        # Generate and apply migrations to create the user table
        res = runner.invoke(cli_module.cli, ["makerevision", auth_app])
        assert res.exit_code == 0

        res = runner.invoke(cli_module.cli, ["upgrade"])
        assert res.exit_code == 0

        # Create the user
        res = runner.invoke(cli_module.cli, ["createuser", "user_1", "1234"])
        assert res.exit_code == 0

    # The CLI should guess if a settings module is present in CWD
    with working_directory(create_project):
        tmp = environ.pop(PROJECT_SETTINGS_MODULE)

        res = runner.invoke(cli_module.cli, ["createuser", "user_2", "1234"])
        assert res.exit_code == 1

        environ[PROJECT_SETTINGS_MODULE] = tmp

    # The command doe not work outside project directory
    with working_directory(create_project.parent):
        tmp = environ.pop(PROJECT_SETTINGS_MODULE)

        res = runner.invoke(cli_module.cli, ["createuser", "user_2", "1234"])
        assert res.exit_code == 1

        environ[PROJECT_SETTINGS_MODULE] = tmp
