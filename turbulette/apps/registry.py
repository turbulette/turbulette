from importlib import import_module
from inspect import ismodule
from types import ModuleType
from typing import Dict, List
from ariadne import snake_case_fallback_resolvers
from graphql.type import GraphQLSchema
from simple_settings import LazySettings
from simple_settings.strategies import SettingsLoadStrategyPython

from turbulette import conf
from turbulette.apps.base import mutation as root_mutation
from turbulette.apps.base import query as root_query
from turbulette.apps.base import subscription as root_subscription
from turbulette.apps.base.resolvers.root_types import base_scalars_resolvers
from turbulette.utils import get_project_settings
from turbulette.conf.constants import (
    SETTINGS_INSTALLED_APPS,
    SETTINGS_LOGS,
    SETTINGS_RULES,
    TURBULETTE_CORE_APPS,
)
from turbulette.validation import pydantic_binder

from .app import TurbuletteApp
from .constants import MODULE_SETTINGS
from .exceptions import RegistryError


class TurbuletteSettingsLoadStrategy(SettingsLoadStrategyPython):
    """A custom strategy to collect all settings rules before processing them."""

    @classmethod
    def load_settings_file(cls, settings_file):
        result = {}
        module = import_module(settings_file)
        # All settings starting with `_` are ignored
        for setting in (s for s in dir(module) if not s.startswith("_")):
            setting_value = getattr(module, setting)
            if setting == SETTINGS_RULES:
                for key, value in setting_value.items():
                    if key == conf.OVERRIDE_BY_ENV:
                        conf.SIMPLE_SETTINGS[key] = value
                    else:
                        conf.SIMPLE_SETTINGS[key].update(value)
            elif setting == SETTINGS_LOGS:
                conf.SIMPLE_SETTINGS[SETTINGS_LOGS] = setting_value
            if not ismodule(setting_value):
                result[setting] = setting_value
        return result


class Registry:
    """A class storing the Turbulette applications in use.

    It mostly serve as a proxy to execute common actions on all apps
    plus some configuration stuff (loading settings, models etc)
    """

    def __init__(
        self,
        path_list: List[str] = None,
        project_settings: str = None,
        project_settings_module: ModuleType = None,
        app_settings_module: str = MODULE_SETTINGS,
    ):
        self.apps: Dict[str, TurbuletteApp] = {}
        self._ready = False

        project_settings_module = (
            import_module(get_project_settings(project_settings))
            if not project_settings_module
            else project_settings_module
        )

        self.project_settings_path = project_settings_module.__name__
        path_list = (
            list(getattr(project_settings_module, SETTINGS_INSTALLED_APPS))
            + TURBULETTE_CORE_APPS
        )

        if path_list:
            for path in path_list:
                g_app = TurbuletteApp(path)
                self.apps.update({g_app.label: g_app})

        self.settings_module = app_settings_module

        self.schema = None

    def get_app_by_label(self, label: str) -> TurbuletteApp:
        """Retrieve the Turbulette app given its label.

        Args:
            label: App label

        Returns:
            TurbuletteApp: The Turbulette application
        """
        try:
            return self.apps[label]
        except KeyError as error:
            raise RegistryError(
                f'App with label "{label}" cannot be found in the registry'
            ) from error

    def get_app_by_package(self, package_name: str) -> TurbuletteApp:
        """Retrieve a Turbulette application given its package path.

        Args:
            path: The module path of the app (dotted path)

        Returns:
            TurbuletteApp: The Turbulette application
        """
        try:
            return self.apps[package_name.rsplit(".", maxsplit=1)[-1]]
        except KeyError as error:
            raise RegistryError(
                f'App with package name "{package_name}" cannot be found in the registry'
            ) from error

    def setup(self) -> GraphQLSchema:
        """Load GraphQL resources and settings for each app and create the global executable schema.

        Returns:
            GraphQLSchema: The aggregated schema from all apps
        """
        settings = self.load_settings()
        if settings.APOLLO_FEDERATION:
            make_schema = getattr(
                import_module("ariadne.contrib.federation"), "make_federated_schema"
            )
        else:
            make_schema = getattr(import_module("ariadne"), "make_executable_schema")
        schema, directives = [], {}
        for app in self.apps.values():
            app.load_graphql_ressources()
            app.load_models()
            pydantic_binder.models.update(app.load_pydantic_models())
            if app.schema:
                schema.extend([*app.schema])
            directives.update(app.directives)

        if not schema:
            raise RegistryError("None of the Turbulette apps have a schema")

        executable_schema = make_schema(
            [*schema],
            root_mutation,
            root_query,
            root_subscription,
            base_scalars_resolvers,
            snake_case_fallback_resolvers,
            pydantic_binder,
            directives=None if directives == {} else directives,
        )
        self.ready = True
        self.schema = executable_schema
        return executable_schema

    def load_models(self):
        """Import GINO models of each app.

        This make the GINO instance aware of all models across installed apps.
        """
        for app in self.apps.values():
            app.load_models()

    def load_settings(self) -> LazySettings:
        """Put Turbulette app settings together in a `LazySettings` object.

        The `LazySettings` object is from `simple_settings` library, which accepts
        multiple modules path during instantiation.

        Returns:
            LazySettings: LazySettings initialized with all settings module found
        """
        if not conf.settings:
            all_settings = []

            for app in self.apps.values():
                if (app.package_path / f"{self.settings_module}.py").is_file():
                    all_settings.append(f"{app.package_name}.{self.settings_module}")

            # Add project settings at last position to let user
            # defined settings overwrite default ones
            all_settings.append(self.project_settings_path)

            settings = LazySettings(*all_settings)
            settings._dict["SIMPLE_SETTINGS"] = conf.SIMPLE_SETTINGS
            settings.strategies = (TurbuletteSettingsLoadStrategy,)
            # Make settings variable availble in the `turbulette.conf` package
            conf.settings = settings

            return settings
        return conf.settings

    def register(self, app: TurbuletteApp):
        """Register an existing [TurbuletteApp][turbulette.apps.app:TurbuletteApp].

        Args:
            app: The [TurbuletteApp][turbulette.apps.app:TurbuletteApp] to add

        Raises:
            RegistryError: Raised if the app is already registered
        """
        if app.label in self.apps:
            raise RegistryError(f'App "{app}" is already registered')
        self.apps[app.label] = app

    @property
    def ready(self) -> bool:
        """The registry is ready if all of its apps are ready."""
        if not self._ready:
            self._ready = all(self.apps.values())
            return self._ready
        return self._ready

    @ready.setter
    def ready(self, value: bool):
        """Once the registry is ready, we cannot make it unready anymore."""
        if not self._ready:
            self._ready = value
        if self._ready and value is not self._ready:
            raise ValueError("Registry cannot be unready as it's already ready")
        self._ready = value
