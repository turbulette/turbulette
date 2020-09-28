from turbulette.core.validation.pyd_model import GraphQLModel


class CreateBook(GraphQLModel):
    __type__ = "CreateBookInput"

    class GraphQL:
        gql_type = "CreateBookInput"


class CreateComics(GraphQLModel):
    __type__ = "CreateComicInput"

    class GraphQL:
        gql_type = "CreateComicInput"


class BookPayload(GraphQLModel):
    __type__ = "BookPayload"

    class GraphQL:
        gql_type = "BookPayload"

    # __type__ = "CreateUser"


class Book(GraphQLModel):
    __type__ = "Book"

    class GraphQL:
        gql_type = "Book"

    # __type__ = "CreateUser"


class Profile(GraphQLModel):
    __type__ = "Profile"

    class GraphQL:
        gql_type = "Profile"
