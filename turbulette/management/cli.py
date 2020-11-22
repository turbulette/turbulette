import asyncio
import configparser
from os import chdir, remove, sep, environ
from pathlib import Path
from pprint import pprint
from shutil import copytree
from types import FunctionType

import click
from alembic.command import revision
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config
from click.exceptions import ClickException
from jwcrypto import jwk

from turbulette import turbulette_starlette
from turbulette.utils import get_project_settings
from turbulette.conf.constants import (
    FILE_ALEMBIC_INI,
    FOLDER_MIGRATIONS,
    PROJECT_SETTINGS_MODULE,
    TEST_MODE,
)

TEMPLATE_FILES = ["app.py", ".env", "settings.py"]

CRV = {
    "OKP": ["Ed25519", "Ed448", "X25519", "X448"],
    "EC": ["P-256", "P-384", "P-521", "secp256k1"],
}

DEFAULT_KTY = "EC"
DEFAULT_CRV = "P-256"


def db(func: FunctionType):
    """Decorator to access database in commands."""

    async def wrap(**kwargs):
        try:
            TEST_MODE not in environ and turbulette_starlette(
                get_project_settings(guess=True)
            )
        except ModuleNotFoundError as error:  # pragma: no cover
            raise click.ClickException(
                "Project settings module not found, are you in the project directory?"
                f" You may want to set the {PROJECT_SETTINGS_MODULE} environment variable."
            ) from error
        from turbulette.conf import (  # pylint: disable=import-outside-toplevel
            db as turb_db,
            settings,
        )

        async with turb_db.with_bind(bind=settings.DB_DSN):
            TEST_MODE in environ and turbulette_starlette(
                get_project_settings(guess=True)
            )
            await func(**kwargs)

    return wrap


def process_tags(file: Path, tags: dict):
    text = file.read_text()
    for tag, value in tags.items():
        text = text.replace(f"{{{{ {tag} }}}}", value)
    file.write_text(text)


def get_alembic_ini():
    alembic_ini = Path.cwd() / FILE_ALEMBIC_INI

    if not alembic_ini.is_file():
        raise click.ClickException(
            f"{FILE_ALEMBIC_INI} not found, are you in the project directory?"
        )
    return alembic_ini


@click.group()
def cli():
    pass


@click.command(help="Create a Turbulette project")
@click.option("--name", "-n", prompt="Project name", help="The project name")
@click.option(
    "--app",
    "-a",
    "first_app",
    help=(
        "Create an app with the given name."
        "Can be passed multiple times to create multiple applications"
    ),
    multiple=True,
)
@click.pass_context
def project(ctx, name, first_app):
    project_dir = Path.cwd() / name
    copytree(Path(__file__).parent / "templates" / "project", project_dir)

    # Generate a default secret key
    jwk_key = jwk.JWK.generate(kty=DEFAULT_KTY, crv=DEFAULT_CRV).export(as_dict=True)

    for file in TEMPLATE_FILES:
        path = project_dir / file
        process_tags(
            path,
            {
                "project": name,
                "settings": f"{name}.settings",
                "SECRET_KEY_KTY": f"SECRET_KEY_KTY={jwk_key['kty']}",
                "SECRET_KEY_CRV": f"SECRET_KEY_CRV={jwk_key['crv']}",
                "SECRET_KEY_D": f"SECRET_KEY_D={jwk_key['d']}",
                "SECRET_KEY_X": f"SECRET_KEY_X={jwk_key['x']}",
                "SECRET_KEY_Y": f"SECRET_KEY_Y={jwk_key['y']}",
            },
        )

    if first_app:
        chdir(project_dir.as_posix())
        ctx.invoke(app_, name=first_app)


@click.command(help="Generate a JSON Web Key to put in the settings.py or .env")
@click.option(
    "--kty",
    "-k",
    type=click.Choice(["RSA", "EC", "OKP", "oct"]),
    help="The key type",
    default="EC",
)
@click.option(
    "--size",
    "-s",
    help="The key size (RSA and oct only)",
    type=int,
    default=None,
)
@click.option(
    "--crv",
    "-c",
    type=click.Choice(CRV["EC"] + CRV["OKP"]),
    help=(f"The curve type (OKP and EC only). OKP : {CRV['OKP']} EC : {CRV['EC']}"),
    default="P-256",
)
@click.option(
    "--exp",
    "-x",
    help="The public exponent (RSA only)",
    type=int,
    default=None,
)
@click.option(
    "--env", "-e", help="Display secret params as env variables", is_flag=True
)
def jwk_(kty, size, crv, exp, env):
    """Generate a JSON Web key."""
    payload = {}

    # Validate options
    if kty in CRV:
        if crv not in CRV[kty]:
            raise ClickException(
                f"--crv is not a valid for the {kty} key type, please choose one of "
                f"{CRV[kty]}"
            )
        payload["crv"] = crv

    elif kty in ["RSA", "oct"]:
        if not size:
            raise ClickException(f"The {kty} key type require the --size option")

        payload["size"] = size

        if kty == "RSA" and exp:
            payload["exp"] = exp

    payload["kty"] = kty

    # Generate the JWK
    jwk_key = jwk.JWK.generate(**payload).export(as_dict=True)

    if env:
        # Normalize secret key params
        env_keys = {}
        for key in jwk_key:
            env_keys[f"SECRET_KEY_{key.upper()}"] = jwk_key[key]

        print(*[f"{key}={value}" for key, value in env_keys.items()], sep="\n")
        print("\nBe sure to update both your .env and settings.py accordingly")
    else:
        pprint(jwk_key)


@click.command(help="Create a Turbulette application")
@click.option(
    "--name",
    "-n",
    help="The app name. Can be passed multiple times to create multiple applications",
    multiple=True,
)
def app_(name):
    for app_name in name:
        alembic_ini = get_alembic_ini()
        copytree(Path(__file__).parent / "templates" / "app", Path.cwd() / app_name)
        for gitkeep in (Path.cwd() / app_name).rglob(".gitkeep"):
            remove(gitkeep)
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
            message="initial",
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


@click.command(help="Create a user using the AUTH_USER_MODEL setting")
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


cli.add_command(project)
cli.add_command(app_, "app")
cli.add_command(upgrade)
cli.add_command(makerevision)
cli.add_command(jwk_, "jwk")
cli.add_command(create_user_cmd, "createuser")
