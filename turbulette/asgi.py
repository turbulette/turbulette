"""Wrap creation of the ASGI app."""

from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import List, Optional, Type

from ariadne.asgi import GraphQL
from ariadne.types import Extension
from caches import Cache
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
from turbulette.errors import error_formatter
from turbulette.extensions import PolicyExtension
from turbulette.utils import get_project_settings, import_class

from .apps import Registry


async def startup():
    await cache.connect()


async def shutdown():
    await cache.disconnect()


def setup(project_settings: str = None) -> GraphQL:
    """Load Turbulette applications and return the GraphQL route."""
    project_settings_module = import_module(get_project_settings(project_settings))

    registry = Registry(project_settings_module=project_settings_module)
    conf.registry.__setup__(registry)
    schema = registry.setup()
    # At this point, settings are now available through
    # `settings` from `turbulette.conf` module
    settings = conf.settings

    # Now that the database connection is established, we can use `settings`

    cache.__setup__(Cache(settings.CACHE))

    extensions: List[Type[Extension]] = [PolicyExtension]
    for ext in settings.ARIADNE_EXTENSIONS:
        module_class = ext.rsplit(".", 1)
        extensions.append(
            getattr(
                import_module(module_class[0]),
                module_class[1],
            )
        )

    graphql_route = GraphQL(
        schema,
        debug=settings.DEBUG,
        extensions=extensions,
        error_formatter=error_formatter,
    )
    return graphql_route


def _register_middlewares() -> List[Middleware]:
    middlewares = []
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
    return middlewares


def turbulette(project_settings: Optional[str] = None) -> Starlette:
    """Setup turbulette apps and mount the GraphQL route on a Starlette instance.

    Args:
        project_settings (str, optional): project settings module name.
        Defaults to None.

    Raises:
        ASGIFrameworkError: Raised if Starlette cannot be imported

    Returns:
        The Starlette instance
    """
    routes = []

    settings_path = get_project_settings(project_settings)
    settings_module = import_module(settings_path)
    db_connection = None

    is_database = hasattr(settings_module, "DATABASES")

    if is_database:
        db_connection = import_class(getattr(settings_module, "DATABASES")["backend"])(
            getattr(settings_module, "DATABASES")["settings"],
            getattr(settings_module, "DATABASES")["connection"],
        )
        db_connection.connect()

    graphql_route = setup(settings_path)
    middlewares = _register_middlewares()

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
