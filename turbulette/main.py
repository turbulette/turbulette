from importlib import import_module
from typing import List, Type

from ariadne.asgi import GraphQL
from ariadne.types import Extension
from caches import Cache
from gino import Gino  # type: ignore [attr-defined]

from turbulette import conf
from turbulette.utils import get_project_settings
from turbulette.cache import cache
from turbulette.errors import error_formatter
from turbulette.extensions import PolicyExtension

from .apps import Registry

# from .apps.config import get_project_settings_by_env


def get_gino_instance() -> Gino:
    if conf.db.initialized:
        return conf.db
    database = Gino()
    conf.db.__setup__(database)
    return database


def setup(project_settings: str = None, database: bool = False) -> GraphQL:
    """Load Turbulette applications and return the GraphQL route."""
    project_settings_module = import_module(get_project_settings(project_settings))

    # The database connection has to be initialized before the LazySettings object to be setup
    # so we have to connect to the database before the registry to be setup
    if database:
        get_gino_instance()

    registry = Registry(project_settings_module=project_settings_module)
    conf.registry.__setup__(registry)
    schema = registry.setup()
    # At this point, settings are now available through `settings` from `turbulette.conf` module
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
