from importlib import import_module
from importlib.util import find_spec
from pathlib import Path

from gino_starlette import Gino
from sqlalchemy.engine.url import URL
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route

from turbulette import conf
from turbulette.conf.constants import (
    ROUTING_MODULE_ROUTES,
    SETTINGS_DATABASE_SETTINGS,
    SETTINGS_DB_DSN,
    TURBULETTE_ROUTING_MODULE,
)
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.main import setup
from turbulette.type import DatabaseSettings


def gino_starlette(settings: DatabaseSettings, dsn: URL):
    """Setup db connection using gino_starlette extension.

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
    conf.db = database
    return database


def turbulette_starlette(project_settings: str):
    """Setup turbulette apps and mount the GraphQL route on a Starlette instance.

    Args:
        project_settings (str, optional): project settings module name. Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if Starlette cannot be imported

    Returns:
        FastAPI: The Starlette instance
    """
    middlewares, routes = [], []

    project_settings_module = import_module(project_settings)

    gino_starlette(
        getattr(project_settings_module, "DATABASE_SETTINGS"),
        getattr(project_settings_module, "DB_DSN"),
    )
    graphql_route = setup(project_settings)

    # Register middlewares
    if conf.settings.MIDDLEWARE_CLASSES:
        for middleware in conf.settings.MIDDLEWARE_CLASSES:
            middlewares.append(
                Middleware(
                    getattr(
                        import_module(middleware.rsplit(".", 1)[0]),
                        middleware.rsplit(".", 1)[1],
                    )
                )
            )

    # Register routes
    spec = find_spec(project_settings)
    if spec and spec.origin:
        if (Path(spec.origin).parent / f"{TURBULETTE_ROUTING_MODULE}.py").is_file():
            routes = getattr(
                import_module(
                    f"{project_settings.split('.',    1)[0]}.{TURBULETTE_ROUTING_MODULE}"
                ),
                ROUTING_MODULE_ROUTES,
            )

        app = Starlette(
            debug=getattr(project_settings_module, "DEBUG"),
            routes=[Route(conf.settings.GRAPHQL_ENDPOINT, graphql_route)] + routes,
            middleware=middlewares,
        )

        conf.app = app
        conf.db.init_app(app)
        return app
    raise ImproperlyConfigured(
        f"Cannot find spec for module {project_settings}"
    )  # pragma: no cover
