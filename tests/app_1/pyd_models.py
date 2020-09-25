from turbulette.core.validation.pyd_model import GraphQLModel


class CreateBook(GraphQLModel):
    __type__ = "CreateBookInput"


class CreateComics(GraphQLModel):
    __type__ = "CreateComicInput"


class BookPayload(GraphQLModel):
    __type__ = "BookPayload"
    # __type__ = "CreateUser"


class Book(GraphQLModel):
    __type__ = "Book"
    # __type__ = "CreateUser"


class Profile(GraphQLModel):
    __type__ = "Profile"
