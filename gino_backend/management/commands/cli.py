import asyncio
from importlib import import_module
from os import environ
from pathlib import Path
from types import FunctionType

import click
from alembic.command import revision
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config

from gino_backend import GinoBackend
from turbulette import conf, turbulette
from turbulette.conf.constants import (
    FILE_ALEMBIC_INI,
    PROJECT_SETTINGS_MODULE,
    TEST_MODE,
)
from turbulette.utils import get_project_settings


def db(func: FunctionType):
    """Decorator to access database in commands."""

    settings_path = get_project_settings(guess=True)
    async def wrap(**kwargs):
        def _load():
            """Wrapper to load a Turbulette instance."""
            try:
                turbulette(settings_path)
            except ModuleNotFoundError as error:  # pragma: no cover
                raise click.ClickException(
                    "Project settings module not found,"
                    "are you in the project directory?"
                    f" You may want to set the {PROJECT_SETTINGS_MODULE}"
                    f" environment variable."
                ) from error

        settings_module = import_module(settings_path)
        url = GinoBackend.make_url(getattr(settings_module, "DATABASES")["connection"])
        # When using this decorator within a test session,
        # the Turbulette db may already exists, so we want
        # to use the existing one.
        if TEST_MODE not in environ:
            _load()  # pragma: no cover
        async with conf.db.with_bind(bind=url):
            if TEST_MODE in environ:
                _load()
            await func(**kwargs)

    return wrap


def get_alembic_ini():
    alembic_ini = Path.cwd() / FILE_ALEMBIC_INI

    if not alembic_ini.is_file():
        raise click.ClickException(
            f"{FILE_ALEMBIC_INI} not found, are you in the project directory?"
        )
    return alembic_ini


@click.command(
    help=(
        "Apply alembic revisions."
        " If an app name is given, upgrade to the latest revision for this app only."
        " If no app is given, upgrade to the latest revision for all apps"
    )
)
@click.argument("app", required=False)
def upgrade(app):
    alembic_ini = get_alembic_ini()
    config = Config(file_=alembic_ini.as_posix())
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
@click.option("--message", "-m", help="Revision message")
def makerevision(app, message):
    alembic_ini = get_alembic_ini()
    config = Config(file_=alembic_ini.as_posix())
    revision(config, message=message, autogenerate=True, head=f"{app}@head")


@click.command(name="create-user", help="Create a user using the AUTH_USER_MODEL setting")
@click.argument("username", nargs=1)
@click.argument("password", nargs=1)
@click.option("--email", "-e", help="User email")
@click.option("--first-name", "-f", help="First name", default=None)
@click.option("--last-name", "-l", help="Last name", default=None)
@click.option(
    "--is-staff", "-s", help="Wether the user is a staff member or not", is_flag=True
)
@click.option("--others", "-o", help="Other fields", default="")
def create_user_cmd(username, password, email, first_name, last_name, is_staff, others):
    # username must be unique so we can use it to generate the email
    email = f"{username}@example.com" if not email else email

    kwargs = {kv.split("=")[0]: kv.split("=")[1] for kv in others.split()}

    @db
    async def _create_user():
        from turbulette.apps.auth.utils import (  # pylint: disable=import-outside-toplevel
            create_user,
        )

        await create_user(
            username=username,
            password_one=password,
            password_two=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            **kwargs,
        )

    # Python 3.6 does not have asyncio.run() (added in 3.7)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_create_user())
