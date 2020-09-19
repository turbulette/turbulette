from importlib import import_module

from ariadne.asgi import GraphQL
from gino import Gino  # type: ignore [attr-defined]

from turbulette import conf
from turbulette.core.errors import error_formatter
from turbulette.core.extensions import PolicyExtension

from .apps import Registry
from .apps.config import get_project_settings_by_env


def get_gino_instance() -> Gino:
    if conf.db:
        return conf.db
    database = Gino()
    conf.db = database
    return database


def setup(project_settings: str = None) -> GraphQL:
    """Load Turbulette applications and return the GraphQL route."""
    project_settings_module = (
        get_project_settings_by_env()
        if not project_settings
        else import_module(project_settings)
    )

    # The database connection has to be initialized before the LazySettings object to be setup
    # so we have to connect to the database before the registry to be setup
    get_gino_instance()

    registry = Registry(project_settings_module=project_settings_module)
    conf.registry = registry
    schema = registry.setup()
    # At this point, settings are now available through `settings` from `turbulette.conf` module
    settings = conf.settings

    # Now that the database connection is established, we can use `settings`

    extensions = [PolicyExtension]
    if settings.APOLLO_TRACING:
        extensions.append(
            getattr(
                import_module("ariadne.contrib.tracing.apollotracing"),
                "ApolloTracingExtension",
            )
        )

    graphql_route = GraphQL(
        schema,
        debug=settings.DEBUG,
        extensions=extensions,
        error_formatter=error_formatter,
    )
    return graphql_route
