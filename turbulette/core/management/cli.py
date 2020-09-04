import configparser
from importlib import import_module
from os import chdir, sep
from pathlib import Path
from pprint import pprint
from shutil import copytree

import click
from alembic.command import revision
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config
from click.exceptions import ClickException
from jwcrypto import jwk

from turbulette.conf.constants import FILE_ALEMBIC_INI, FOLDER_MIGRATIONS

TEMPLATE_FILES = [Path("app.py"), Path("alembic") / "env.py"]

CRV = {
    "OKP": ["Ed25519", "Ed448", "X25519", "X448"],
    "EC": ["P-256", "P-384", "P-521", "secp256k1"],
}


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
@click.option("--name", "-n", prompt="Project name", help="The project name")
@click.option(
    "--app",
    "-a",
    help=(
        "Create an app with the given name."
        "Can be passed multiple times to create multiple applications"
    ),
    multiple=True,
)
@click.pass_context
def create_project(ctx, name, app):
    project_dir = Path.cwd() / name
    copytree(Path(__file__).parent / "templates" / "project", project_dir)
    for file in TEMPLATE_FILES:
        path = project_dir / file
        process_tags(path, {"settings": f"{name}.settings"})
    if app:
        chdir(project_dir.as_posix())
        ctx.invoke(create_app, name=app)


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
def secret_key(kty, size, crv, exp, env):
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
@click.option("--message", "-m", help="Revision message")
def makerevision(app, message):
    alembic_ini = get_alembic_ini()
    config = Config(file_=alembic_ini.as_posix())
    revision(config, message=message, autogenerate=True, head=f"{app}@head")


cli.add_command(create_project)
cli.add_command(create_app)
cli.add_command(upgrade)
cli.add_command(makerevision)
cli.add_command(secret_key)
