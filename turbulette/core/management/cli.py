import configparser
from os import sep
from pathlib import Path
from shutil import copytree
from importlib import import_module
import click
from alembic.config import Config
from alembic.command import revision, upgrade as alembic_upgrade
from turbulette.conf.constants import (
    FILE_ALEMBIC_INI,
    FOLDER_MIGRATIONS,
)


TEMPLATE_FILES = [Path("app.py"), Path("alembic") / "env.py"]


def process_tags(file: Path, tags: dict):
    text = file.read_text()
    for tag, value in tags.items():
        text = text.replace(f"{{{{ {tag} }}}}", value)
    file.write_text(text)


def get_alembic_ini():
    alembic_ini = Path.cwd() / FILE_ALEMBIC_INI

    if not alembic_ini.is_file():
        raise click.ClickException(
            f"{FILE_ALEMBIC_INI} not found, are you in a project directory?"
        )
    return alembic_ini


@click.group()
def cli():
    pass


@click.command(help="Create a Turbulette project")
@click.option("--name", prompt="Project name", help="The project name")
def create_project(name):
    project_dir = Path.cwd() / name
    copytree(Path(__file__).parent / "templates" / "project", project_dir)
    for file in TEMPLATE_FILES:
        path = project_dir / file
        process_tags(path, {"settings": f"{name}.settings"})


@click.command(help="Create a Turbulette application")
@click.option("--name", "-n", prompt="App name", help="The app name. Can be passed multiple times to create multiple applications", multiple=True)
def create_app(name):
    for app_name in name:
        alembic_ini = get_alembic_ini()
        copytree(Path(__file__).parent / "templates" / "app", Path.cwd() / app_name)

        alembic_config = configparser.ConfigParser(interpolation=None)
        alembic_config.read(alembic_ini)
        migration_dir = f"%(here)s{sep}{app_name}{sep}{FOLDER_MIGRATIONS}"

        if "version_locations" in alembic_config["alembic"]:
            alembic_config["alembic"]["version_locations"] += f" {migration_dir}"
        else:
            alembic_config["alembic"]["version_locations"] = migration_dir

        with open(alembic_ini, "w") as alembic_file:
            alembic_config.write(alembic_file)

        config = Config(file_=alembic_ini.as_posix())

        revision(
            config,
            message=f"create app {app_name} branch",
            head="base",
            branch_label=app_name,
            version_path=(Path(app_name) / FOLDER_MIGRATIONS).as_posix(),
        )


@click.command(
    help=(
        "Apply alembic revisions."
        " If an app name is given, upgrade to the latest revision for this app only."
        " If no app is given, upgrade to the latest revision for all apps in the current project"
    )
)
@click.argument("app", required=False)
def upgrade(app):
    alembic_ini = get_alembic_ini()
    config = Config(file_=alembic_ini.as_posix())
    settings = import_module(f"{alembic_ini.parent.name}.settings")
    config.set_main_option("sqlalchemy.url", str(settings.DB_DSN))
    if not app:
        alembic_upgrade(config, "heads")
    else:
        alembic_upgrade(config, f"{app}@head")


@click.command(
    help=(
        "Autogenerate alembic revision for the given app."
        " This is a shortcut to `alembic revision --autogenerate --head=<app>@head`"
    )
)
@click.argument("app", required=True, nargs=1)
@click.option("--message/-m", help="Revision message")
def makerevision(app, message):
    alembic_ini = get_alembic_ini()
    config = Config(file_=alembic_ini.as_posix())
    revision(config, message=message, autogenerate=True, head=f"{app}@head")


cli.add_command(create_project)
cli.add_command(create_app)
cli.add_command(upgrade)
cli.add_command(makerevision)
