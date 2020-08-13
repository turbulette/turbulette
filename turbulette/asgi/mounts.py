from importlib import import_module
from typing import Dict, Union

from sqlalchemy.engine.url import URL
from starlette.config import Config

from turbulette import conf
from turbulette.conf.constants import SETTINGS_DATABASE_SETTINGS, SETTINGS_DB_DSN
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.main import setup

from .exceptions import ASGIFrameworkError, GinoExtensionError


def gino_starlette(settings: Dict[str, Union[Config, str]], dsn: URL):
    try:
        from gino_starlette import Gino
    except ModuleNotFoundError:
        raise GinoExtensionError("Failed to import gino_starlette, is it installed?")

    if not settings:
        raise ImproperlyConfigured(
            f"You did not set the {SETTINGS_DATABASE_SETTINGS} setting"
        )
    if not dsn:
        raise ImproperlyConfigured(f"You did not set the {SETTINGS_DB_DSN} setting")
    try:
        database = Gino(
            dsn=dsn,
            pool_min_size=settings["DB_POOL_MIN_SIZE"],
            pool_max_size=settings["DB_POOL_MAX_SIZE"],
            echo=settings["DB_ECHO"],
            ssl=settings["DB_SSL"],
            use_connection_for_request=settings["DB_USE_CONNECTION_FOR_REQUEST"],
            retry_limit=settings["DB_RETRY_LIMIT"],
            retry_interval=settings["DB_RETRY_INTERVAL"],
        )
    except KeyError as error:
        raise ImproperlyConfigured(
            f"You did not set {error.args[0]} in {SETTINGS_DATABASE_SETTINGS}"
        )
    conf.db = database
    return database


def turbulette_fastapi(project_settings: str = None):
    """Setup turbulette apps and mount the graphql route on a FastAPI instance

    Args:
        project_settings (str, optional): project settings module name. Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if FastAPI cannot be imported

    Returns:
        FastAPI: The FastAPI instance
    """
    try:
        from fastapi import FastAPI
    except ModuleNotFoundError:
        raise ASGIFrameworkError("Failed to import FastAPI, is it installed?")

    project_settings_module = import_module(project_settings)
    db = gino_starlette(
        project_settings_module.DATABASE_SETTINGS, project_settings_module.DB_DSN
    )
    graphql_route = setup(project_settings)
    app = FastAPI()
    app.mount(conf.settings.GRAPHQL_ENDPOINT, graphql_route)
    conf.db.init_app(app)
    return app


def turbulette_starlette(project_settings: str = None):
    """Setup turbulette apps and mount the graphql route on a FastAPI instance

    Args:
        project_settings (str, optional): project settings module name. Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if Starlette cannot be imported

    Returns:
        FastAPI: The Starlette instance
    """
    try:
        from starlette.applications import Starlette
        from starlette.routing import Route
    except ModuleNotFoundError:
        raise ASGIFrameworkError("Failed to import starlette, is it installed?")

    project_settings_module = import_module(project_settings)
    db = gino_starlette(
        project_settings_module.DATABASE_SETTINGS, project_settings_module.DB_DSN
    )
    graphql_route = setup(project_settings)
    app = Starlette(
        debug=conf.settings.DEBUG,
        routes=[Route(conf.settings.GRAPHQL_ENDPOINT, graphql_route),],
    )
    db.init_app(app)
    return app
