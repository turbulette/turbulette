"""Turbulette's command line tool."""

import sys
from os import chdir, environ, remove
from pathlib import Path
from pprint import pprint
from shutil import copytree

import click
import cloup
from click.exceptions import ClickException
from jwcrypto import jwk

from turbulette.apps import Registry
from turbulette.conf.constants import PROJECT_SETTINGS_MODULE
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.utils import get_project_settings, to_dotted_path

TEMPLATE_FILES = ["app.py", ".env", "settings.py"]

CRV = {
    "OKP": ["Ed25519", "Ed448", "X25519", "X448"],
    "EC": ["P-256", "P-384", "P-521", "secp256k1"],
}

DEFAULT_KTY = "EC"
DEFAULT_CRV = "P-256"


def process_tags(file: Path, tags: dict):
    text = file.read_text()
    for tag, value in tags.items():
        text = text.replace(f"{{{{ {tag} }}}}", value)
    file.write_text(text)


@cloup.group("Turbulette")
# Hacky solution to make it appear in help message,
# but the option will never be parsed by click
@click.option("--settings", "-s", help="Project settings module")
def cli(settings):
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


@click.command(
    name="jwk", help="Generate a JSON Web Key to put in the settings.py or .env"
)
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


@click.command(name="app", help="Create a Turbulette application")
@click.option(
    "--name",
    "-n",
    help="The app name. Can be passed multiple times to create multiple applications",
    multiple=True,
)
def app_(name):
    for app_name in name:
        # alembic_ini = get_alembic_ini()
        copytree(Path(__file__).parent / "templates" / "app", Path.cwd() / app_name)
        for gitkeep in (Path.cwd() / app_name).rglob(".gitkeep"):
            remove(gitkeep)


cli.section("Turbulette", project, app_, jwk_)

# Parse --settings option manually
# as it's needed to get the registry
settings_path_str, settings_path, settings_module = None, None, None

if sys.argv[1] in ["--settings", "-s"]:
    settings_path_str = sys.argv[2]
    sys.argv.pop(1)
    sys.argv.pop(1)
elif sys.argv[1].startswith("--settings="):
    settings_path_str = sys.argv[1].split("--settings=")[1]
    sys.argv.pop(1)

if settings_path_str:
    settings_path = Path(settings_path_str).resolve()
    if not settings_path.is_file():
        raise click.ClickException("The provided settings module does not exist")
    settings_module = to_dotted_path(settings_path.relative_to(Path.cwd()))

try:
    settings_module = get_project_settings(settings_module, guess=True)
    environ.setdefault(PROJECT_SETTINGS_MODULE, settings_module)
    registry = Registry(settings_path=settings_module)

    for app, cmds in registry.load_cmds().items():
        cli.section(app, *cmds)
except ImproperlyConfigured:
    pass
