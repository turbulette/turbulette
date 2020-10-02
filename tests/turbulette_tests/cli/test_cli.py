from tempfile import TemporaryDirectory

from click.testing import CliRunner

from turbulette.management.cli import cli

from .conftest import APP_1, APP_2, working_directory


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


def test_not_a_project_dir():
    runner = CliRunner()
    with TemporaryDirectory() as tmp_dir:
        with working_directory(tmp_dir):
            res = runner.invoke(cli, ["app", "--name", "app_1"])
            assert res.exit_code != 0


def test_create_app(create_project):
    with working_directory(create_project):
        runner = CliRunner()
        res = runner.invoke(cli, ["app", "--name", "app_1"])
        assert res.exit_code == 0
        res = runner.invoke(cli, ["app", "--name", "app_2", "--name", "app_3"])
        assert res.exit_code == 0


def test_upgrade(create_project, create_db_cli, create_apps):
    with working_directory(create_project):
        runner = CliRunner()
        res = runner.invoke(cli, ["upgrade", APP_1])
        assert res.exit_code == 0
        # Should upgrade APP_2 and APP_3
        res = runner.invoke(cli, ["upgrade"])
        assert res.exit_code == 0


def test_makerevision(create_project, create_db_cli, create_apps):
    with working_directory(create_project):
        runner = CliRunner()
        res = runner.invoke(cli, ["makerevision", APP_2])
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
