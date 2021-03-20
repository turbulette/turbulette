"""Wrap creation of the ASGI app."""

from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Route, WebSocketRoute

from turbulette import conf
from turbulette.cache import cache
from turbulette.conf.constants import (
    ROUTING_MODULE_ROUTES,
    SETTINGS_MIDDLEWARES,
    TURBULETTE_ROUTING_MODULE,
)
from turbulette.conf.exceptions import ImproperlyConfigured
from turbulette.main import setup
from turbulette.utils import get_project_settings, import_class


async def startup():
    await cache.connect()


async def shutdown():
    await cache.disconnect()


def turbulette_starlette(project_settings: Optional[str] = None) -> Starlette:
    """Setup turbulette apps and mount the GraphQL route on a Starlette instance.

    Args:
        project_settings (str, optional): project settings module name.
        Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if Starlette cannot be imported

    Returns:
        The Starlette instance
    """
    middlewares, routes = [], []

    settings_path = get_project_settings(project_settings)
    settings_module = import_module(settings_path)
    db_connection = None

    is_database = hasattr(settings_module, "DATABASES")

    # and getattr(settings_module, SETTINGS_DATABASE_CONNECTION)[
    #     "DB_HOST"
    # ]  # type: ignore

    if is_database:
        db_connection = import_class(getattr(settings_module, "DATABASES")["backend"])(
            getattr(settings_module, "DATABASES")["settings"],
            getattr(settings_module, "DATABASES")["connection"],
        )
        db_connection.connect()

    graphql_route = setup(settings_path)

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
        if db_connection:
            db_connection.on_startup(app)
            conf.db.__setup__(db_connection.database)
        return app

    raise ImproperlyConfigured(
        f"Cannot find spec for module {settings_path}"
    )  # pragma: no cover
