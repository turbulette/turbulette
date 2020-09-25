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
    __type__: Optional[str] = None
    __initialized__: bool = False

    class Config:
        """Needed to reference custom GraphQL types."""

        orm_mode = True

    @classmethod
    def add_fields(cls, **field_definitions: Tuple) -> None:
        """Add fields to the model.

        adapted from here : https://github.com/samuelcolvin/pydantic/issues/1937#issuecomment-695313040
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
    def __init__(
        self, models: Dict[str, Type[GraphQLModel]]
    ):  # pylint: disable=super-init-not-called
        self.models = models

    def resolve_field_type(
        self, gql_field, schema: GraphQLSchema
    ) -> Tuple[Any, Optional[Any]]:
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
            field_type, _ = self.resolve_field_type(gql_field.of_type, schema)
            # Ellipsis as default value in the pydantic model mark the field as required
            default_value = ...
        elif isinstance(gql_field, GraphQLScalarType):
            field_type = TYPE_MAP[gql_field.name]
        elif isinstance(gql_field, GraphQLList):
            of_type, default_of_type = self.resolve_field_type(
                gql_field.of_type, schema
            )
            if default_of_type is None:
                of_type = Optional[of_type]
            field_type = List[of_type]  # type: ignore
        return field_type, default_value

    def resolve_model_fields(
        self, gql_type: Any, schema: GraphQLSchema
    ) -> Dict[str, Any]:
        pyd_fields = {}
        for name, field in gql_type.fields.items():
            field_type, default_value = self.resolve_field_type(field.type, schema)
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
        for model in self.models.values():
            self.process_model(model, schema)
