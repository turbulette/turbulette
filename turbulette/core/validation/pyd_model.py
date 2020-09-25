from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from ariadne.types import SchemaBindable
from graphql.type.definition import (
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
)
from graphql.type.schema import GraphQLSchema
from pydantic.fields import ModelField
from pydantic.main import BaseModel
from turbulette.utils.normalize import camel_to_snake
from .exceptions import PydanticBindError

# Base mapping for GraphQL types as well as Turbulette built-in scalars
TYPE_MAP = {
    "ID": Union[int, str],
    "String": str,
    "Int": int,
    "Boolean": bool,
    "Float": float,
    "DateTime": datetime,
    "JSON": dict,
}


class GraphQLModel(BaseModel):
    """Base pydantic model for GraphQL type binding.

    The GraphQL type must be assigned to `__type__` when subclassing.
    `__initialized__` is used at binding time, to avoid the model to be processed multiple times.
    (ex : when the GraphQL type is referenced by fields of other GraphQL types)
    """

    __type__: Optional[str] = None
    __initialized__: bool = False

    class Config:
        """Needed to reference custom GraphQL types."""

        orm_mode = True

    @classmethod
    def add_fields(cls, **field_definitions: Tuple) -> None:
        """Add fields to the model.

        Adapted from here :
        https://github.com/samuelcolvin/pydantic/issues/1937#issuecomment-695313040
        """
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}

        for f_name, f_def in field_definitions.items():
            f_annotation, f_value = f_def

            new_fields[f_name] = ModelField.infer(
                name=f_name,
                value=f_value,
                annotation=f_annotation,
                class_validators=None,
                config=cls.__config__,
            )

        cls.__fields__.update(new_fields)
        cls.__annotations__.update(new_annotations)


class PydanticBindable(SchemaBindable):
    """Hold logic to bind GraphQL types to pydantic model."""

    def __init__(
        self, models: Dict[str, Type[GraphQLModel]] = None
    ):  # pylint: disable=super-init-not-called
        """Instantiate the bindable with all pydantic models.

        Args:
            models (Dict[str, Type[GraphQLModel]]): A mapping with GraphQL types as keys
                and pydantic models as values
        """
        self.models = models if models else {}
        self._type_map = {**TYPE_MAP}

    def register_scalar(self, name: str, typing: Any) -> None:
        """Register a custom scalar to use when binding pydantic models.

        Args:
            name (str): Scalar name, must match the one the schema
            typing (Any): Python typing for the scalar
        """
        self._type_map[name] = typing

    def resolve_field_typing(
        self, gql_field, schema: GraphQLSchema
    ) -> Tuple[Any, Optional[Any]]:
        """Find out the proper typing to use for a given GraphQL field.

        Args:
            gql_field ([type]): The GraphQL for which to find typing
            schema (GraphQLSchema): GraphQL schema

        Raises:
            PydanticBindError: Raised when the GraphQL field type is a custom type for which
                no pydantic model has been defined.

        Returns:
            Tuple[Any, Optional[Any]]: A tuple `(typing, default_value)` to pass to `add_fields`.
        """
        field_type: Any = None
        default_value = None

        if isinstance(gql_field, (GraphQLObjectType, GraphQLInputObjectType)):
            sub_model: Optional[Type[GraphQLModel]] = self.models.get(gql_field.name)
            if not sub_model:
                raise PydanticBindError(
                    f'There is no pydantic model binded to "{gql_field.name}" GraphQL type'
                )
            if not sub_model.__initialized__:
                self.process_model(sub_model, schema)
            field_type = sub_model
        elif isinstance(gql_field, GraphQLNonNull):
            field_type, _ = self.resolve_field_typing(gql_field.of_type, schema)
            # Ellipsis as default value in the pydantic model mark the field as required
            default_value = ...
        elif isinstance(gql_field, GraphQLScalarType):
            field_type = self._type_map.get(gql_field.name)
        elif isinstance(gql_field, GraphQLList):
            of_type, default_of_type = self.resolve_field_typing(
                gql_field.of_type, schema
            )
            if default_of_type is None:
                of_type = Optional[of_type]
            field_type = List[of_type]  # type: ignore
        return field_type, default_value

    def resolve_model_fields(
        self, gql_type: Any, schema: GraphQLSchema
    ) -> Dict[str, Any]:
        """Translate fields from a GraphQL type into pydantic ones.

        Args:
            gql_type (Any): GraphQL type on which to translate fields
            schema (GraphQLSchema): GraphQL schema

        Raises:
            PydanticBindError: Raised when a fields can't be translated

        Returns:
            Dict[str, Any]: A dict with pydantic field names as keys and pydantic fields as values.

        All field names are converted to snake_case
        """
        pyd_fields = {}
        for name, field in gql_type.fields.items():
            field_type, default_value = self.resolve_field_typing(field.type, schema)
            if field_type is None:
                raise PydanticBindError(
                    f'Don\'t know how to map "{name}" field from GraphQL type {gql_type.name}'
                )
            if default_value is None:
                field_type = Optional[field_type]
                # Convert names to snake case
            pyd_fields[camel_to_snake(name)] = (field_type, default_value)
        return pyd_fields

    def process_model(self, model: Type[GraphQLModel], schema: GraphQLSchema) -> None:
        """Add fields to the given pydantic model.

        Args:
            model (Type[GraphQLModel]): The pydantic model on which to add fields
            schema (GraphQLSchema): GraphQL schema

        Raises:
            PydanticBindError: Raised if `__type__` is None or
                if no corresponding GraphQL type has been found.
        """
        if not model.__type__:
            raise PydanticBindError(
                f"Can't find __type__ on pydantic model {model.__name__}."
                " You must define __type__ when subclassing GraphQLToPydantic"
                " to bind the model to a GraphQL type."
            )
        type_ = schema.type_map.get(model.__type__)
        if not type_:
            raise PydanticBindError(
                f"The GraphQL type {model.__type__} does not exists"
            )
        if not model.__initialized__:
            fields = self.resolve_model_fields(type_, schema)
            model.__initialized__ = True
            model.add_fields(**fields)

    def bind_to_schema(self, schema: GraphQLSchema) -> None:
        """Called by `make_executable_schema`."""
        for model in self.models.values():
            self.process_model(model, schema)
