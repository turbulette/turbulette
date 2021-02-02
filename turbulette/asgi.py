from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from gino_starlette import Gino
from sqlalchemy.engine.url import URL
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, WebSocketRoute

from turbulette import conf
from turbulette.conf.constants import (
    ROUTING_MODULE_ROUTES,
    SETTINGS_DATABASE_SETTINGS,
    SETTINGS_DB_DSN,
    TURBULETTE_ROUTING_MODULE,
    SETTINGS_DATABASE_CONNECTION,
    SETTINGS_MIDDLEWARES,
)
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.main import setup
from turbulette.type import DatabaseSettings
from turbulette.cache import cache
from turbulette.utils import get_project_settings


def gino_starlette(settings: DatabaseSettings, dsn: URL) -> Gino:
    """Setup db connection using `gino_starlette` extension.

    Args:
        settings (DatabaseSettings): Settings to use when establishing the connection
        dsn (URL): db credentials

    Raises:
        ImproperlyConfigured: Raised if either `settings` or `dsn`
                              are incorrect or have missing values

    Returns:
        The GINO instance
    """
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
        ) from error
    conf.db.__setup__(database)
    return database


async def startup():
    await cache.connect()


async def shutdown():
    await cache.disconnect()


def turbulette_starlette(project_settings: Optional[str] = None) -> Starlette:
    """Setup turbulette apps and mount the GraphQL route on a Starlette instance.

    Args:
        project_settings (str, optional): project settings module name. Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if Starlette cannot be imported

    Returns:
        The Starlette instance
    """
    middlewares, routes = [], []

    settings_path = get_project_settings(project_settings)
    settings_module = import_module(settings_path)

    is_database = (
        hasattr(settings_module, SETTINGS_DATABASE_CONNECTION)
        and getattr(settings_module, SETTINGS_DATABASE_CONNECTION)["DB_HOST"]  # type: ignore
    )

    if is_database:
        gino_starlette(
            getattr(settings_module, SETTINGS_DATABASE_SETTINGS),
            getattr(settings_module, SETTINGS_DB_DSN),
        )

    graphql_route = setup(settings_path, is_database)

    # Register middlewares
    if hasattr(conf.settings, SETTINGS_MIDDLEWARES):
        middleware_list = list(conf.settings.MIDDLEWARES)

        for middleware in middleware_list:
            package, class_ = middleware.rsplit(".", 1)
            middleware_settings = (
                getattr(conf.settings, class_) if hasattr(conf.settings, class_) else {}
            )
            middlewares.append(
                Middleware(
                    getattr(
                        import_module(package),
                        class_,
                    ),
                    **middleware_settings,
                )
            )

    # Register routes
    spec = find_spec(settings_path)
    if spec and spec.origin:
        if (Path(spec.origin).parent / f"{TURBULETTE_ROUTING_MODULE}.py").is_file():
            routes = getattr(
                import_module(
                    f"{settings_path.split('.',    1)[0]}.{TURBULETTE_ROUTING_MODULE}"
                ),
                ROUTING_MODULE_ROUTES,
            )

        app = Starlette(
            debug=getattr(settings_module, "DEBUG"),
            routes=[
                Route(conf.settings.GRAPHQL_ENDPOINT, graphql_route),
                WebSocketRoute(conf.settings.GRAPHQL_ENDPOINT, graphql_route),
            ]
            + routes,
            middleware=middlewares,
            on_startup=[startup],
            on_shutdown=[shutdown],
        )

        conf.app.__setup__(app)
        if is_database:
            conf.db.init_app(app)
        return app

    raise ImproperlyConfigured(
        f"Cannot find spec for module {settings_path}"
    )  # pragma: no cover
