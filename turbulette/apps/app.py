from importlib import import_module
from importlib.util import find_spec
from inspect import getmembers, isclass
from os import sep
from pathlib import Path
from typing import Dict, List, Type

from ariadne import SchemaDirectiveVisitor, load_schema_from_path
from pydantic import BaseModel

from turbulette.validation.pyd_model import GraphQLModel

from .constants import (
    FOLDER_SCHEMA,
    MODULE_DIRECTIVES,
    MODULE_MODELS,
    MODULE_PYDANTIC,
    MODULE_SETTINGS,
    PACKAGE_RESOLVERS,
)
from .exceptions import TurbuletteAppError


def _star_import(module_path: str):
    """Perform a star import from the specified module path.

        This is equivalent to ``from module import *``

        https://stackoverflow.com/a/44492879/10735573

    Args:
        module_path (str): Module path from which to perform the import

    """
    module = import_module(module_path)
    globals().update(
        {n: getattr(module, n) for n in getattr(module, "__all__")}
        if hasattr(module, "__all__")
        else {k: v for (k, v) in module.__dict__.items() if not k.startswith("_")}
    )


class TurbuletteApp:
    """Class representing a Turbulette application."""

    __slots__ = (
        "label",
        "package_name",
        "package_path",
        "schema",
        "directives",
        "schema_folder",
        "resolvers_package",
        "directives_module",
        "models_module",
        "settings_module",
        "ready",
        "pydantic_module",
    )

    def __init__(
        self,
        package: str,
        label: str = None,
        schema: List[str] = None,
        directives: Dict[str, Type[SchemaDirectiveVisitor]] = None,
        schema_folder: str = FOLDER_SCHEMA,
        resolvers_package: str = PACKAGE_RESOLVERS,
        models_module: str = MODULE_MODELS,
        directives_module: str = MODULE_DIRECTIVES,
        settings_module: str = MODULE_SETTINGS,
        pydantic_module: str = MODULE_PYDANTIC,
    ):
        self.package_name = package
        self.label = package.rsplit(".", maxsplit=1)[-1] if label is None else label

        spec = find_spec(self.package_name)

        # If the path doesn't exists we cannot load GraphQL resources
        if not spec or not spec.submodule_search_locations:
            raise TurbuletteAppError(self.label, "Cannot find the module path")

        # Cast to a list ensure its indexable if `submodule_search_locations` is a _NamespacePath
        self.package_path = Path(list(spec.submodule_search_locations)[0])

        self.schema = schema
        self.directives = {} if directives is None else directives

        self.schema_folder = schema_folder
        self.resolvers_package = resolvers_package
        self.models_module = models_module
        self.directives_module = directives_module
        self.settings_module = settings_module
        self.pydantic_module = pydantic_module
        self.ready = False

    def load_resolvers(self):
        """Load resolvers.

        This assumes that all python files under the ``resolvers`` contains resolvers
        functions. Functions that are not binded to a GraphQL query should live outside
        this folder.
        """
        resolver_modules = [
            m.as_posix()[:-3]
            .replace(sep, ".")
            .split(f"{self.package_name}.{self.resolvers_package}.")[1]
            for m in (self.package_path / f"{self.resolvers_package}").rglob("*.py")
        ]

        if len(resolver_modules) > 0:
            for module in resolver_modules:
                # Relative import
                import_module(
                    f".{module}", f"{self.package_name}.{self.resolvers_package}"
                )

    def load_models(self):
        """Load GINO models."""
        if (self.package_path / f"{self.models_module}.py").is_file():
            _star_import(f"{self.package_name}.{self.models_module}")

    def load_directives(self):
        """Load GraphQL directives.
        Directives class must have a class attribute ``name``
        that match the directive name in the GraphQL schema
        """
        if (
            not self.directives
            and (self.package_path / f"{self.directives_module}.py").is_file()
        ):
            # Relative import
            app_directives_module = import_module(
                f".{self.directives_module}", f"{self.package_name}"
            )
            for _, member in getmembers(app_directives_module, isclass):
                if (
                    issubclass(member, SchemaDirectiveVisitor)
                    and member is not SchemaDirectiveVisitor
                ):
                    self.directives[member.name] = member

    def load_schema(self):
        """Load GraphQL schema."""
        if (self.package_path / self.schema_folder).is_dir() and self.schema is None:
            type_defs = [
                load_schema_from_path(self.package_path / f"{self.schema_folder}")
            ]
            if type_defs:
                self.schema = [*type_defs]

    def load_graphql_ressources(self):
        """Load all needed resources to enable GraphQL queries."""
        self.load_schema()
        self.load_directives()
        self.load_resolvers()
        self.ready = True

    def load_pydantic_models(self) -> Dict[str, Type[GraphQLModel]]:
        models: Dict[str, Type[GraphQLModel]] = {}
        if (self.package_path / f"{self.pydantic_module}.py").is_file():
            module = import_module(f".{self.pydantic_module}", f"{self.package_name}")
            for _, member in getmembers(module, isclass):
                if (
                    issubclass(member, BaseModel)
                    and hasattr(member, "GraphQL")
                    and member is not BaseModel
                    and member is not GraphQLModel
                ):
                    models[member.GraphQL.gql_type] = member
        return models

    def __bool__(self):
        """An app is True if it's ready."""
        return self.ready

    def __repr__(self):
        """Standard repr : <TurbuletteApp>: package_name."""
        return f"<{type(self).__name__}: {self.package_name}>"

    def __str__(self):
        """Should be enough to identify an app since the registry store them in a dict."""
        return self.label
