"""Pydantic models used for input validation."""

from turbulette.validation.pyd_model import GraphQLModel


class CreateBook(GraphQLModel):
    class GraphQL:
        gql_type = "CreateBookInput"


class CreateComics(GraphQLModel):
    class GraphQL:
        gql_type = "CreateComicInput"


class BookPayload(GraphQLModel):
    class GraphQL:
        gql_type = "BookPayload"


class Book(GraphQLModel):
    class GraphQL:
        gql_type = "Book"


class Profile(GraphQLModel):
    class GraphQL:
        gql_type = "Profile"
