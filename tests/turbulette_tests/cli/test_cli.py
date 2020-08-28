import os
from os import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
from click.testing import CliRunner
from turbulette.core.management.cli import cli

from .conftest import APP_1, APP_2, PROJECT


def test_create_project():
    runner = CliRunner()
    res = runner.invoke(cli, ["create-project", "--name", PROJECT])
    assert res.exit_code == 0


def test_not_a_project_dir():
    runner = CliRunner()
    old = Path.cwd()
    tmp_dir = TemporaryDirectory()
    chdir(tmp_dir.name)
    res = runner.invoke(cli, ["create-app", "--name", APP_1])
    assert res.exit_code != 0
    tmp_dir.cleanup()
    os.chdir(old)


def test_create_app():
    old = Path.cwd()
    os.chdir(PROJECT)
    runner = CliRunner()
    res = runner.invoke(cli, ["create-app", "--name", APP_1])
    assert res.exit_code == 0
    res = runner.invoke(cli, ["create-app", "--name", APP_2])
    assert res.exit_code == 0
    os.chdir(old)


def test_upgrade(create_db_cli):
    runner = CliRunner()
    old = Path.cwd()
    os.chdir(PROJECT)
    res = runner.invoke(cli, ["upgrade", APP_1])
    assert res.exit_code == 0
    # Should upgrade APP_2
    res = runner.invoke(cli, ["upgrade"])
    assert res.exit_code == 0
    os.chdir(old)


def test_makerevision(create_db_cli):
    runner = CliRunner()
    old = Path.cwd()
    os.chdir(PROJECT)
    res = runner.invoke(cli, ["makerevision", APP_1])
    assert res.exit_code == 0
    os.chdir(old)
