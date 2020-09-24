from turbulette.core.validation.pyd_model import GraphQLToPydantic


class CreateBook(GraphQLToPydantic):
    __type__ = "CreateBookInput"


class CreateComics(GraphQLToPydantic):
    __type__ = "CreateComicInput"


class BookPayload(GraphQLToPydantic):
    __type__ = "BookPayload"
    # __type__ = "CreateUser"


class Book(GraphQLToPydantic):
    __type__ = "Book"
    # __type__ = "CreateUser"


class Profile(GraphQLToPydantic):
    __type__ = "Profile"
