import pytest
from ariadne import make_executable_schema, snake_case_fallback_resolvers, gql
from turbulette.apps.base.resolvers.root_types import base_scalars_resolvers
from turbulette.core.validation import GraphQLModel, PydanticBindable
from turbulette.core.validation.exceptions import PydanticBindError

schema = gql(
    """
scalar Date
scalar DateTime
scalar JSON

type Query {
  _: Boolean
}

type Mutation {
  _: Boolean
}

type GraphQLTypes {
    int: Int!
    float: Float
    string: String
    bool: Boolean
    id: ID

}

type Book {
    id: ID
    title: String!
    author: String
    borrowings: Int
}

type User {
    username: String
    isStaff: Boolean
    hasBorrowed: [Book]
    favBook: Book
    dateJoined: DateTime
    profile: JSON
}

type Foo {
    json: JSON
}

"""
)


def test_graphql_types():
    """Test pydantic bindings."""

    class GraphQLTypes(GraphQLModel):
        __type__ = "GraphQLTypes"

    bindable = PydanticBindable({"GraphQLTypes": GraphQLTypes})
    make_executable_schema(
        schema,
        base_scalars_resolvers,
        snake_case_fallback_resolvers,
        bindable,
    )
    book_schema = GraphQLTypes.schema()
    book_schema.pop("description")
    assert book_schema == {
        "properties": {
            "id": {
                "title": "Id",
                "anyOf": [{"type": "integer"}, {"type": "string"}],
            },
            "string": {"title": "String", "type": "string"},
            "int": {"title": "Int", "type": "integer"},
            "float": {"title": "Float", "type": "number"},
            "bool": {"title": "Bool", "type": "boolean"},
        },
        "required": ["int"],
        "title": "GraphQLTypes",
        "type": "object",
    }
    GraphQLTypes(int=1)

    with pytest.raises(ValueError):
        GraphQLTypes()


def test_referencing():
    class Book(GraphQLModel):
        __type__ = "Book"

    class User(GraphQLModel):
        __type__ = "User"

    bindable = PydanticBindable({"Book": Book, "User": User})
    make_executable_schema(
        schema,
        base_scalars_resolvers,
        snake_case_fallback_resolvers,
        bindable,
    )
    book = {"title": "random"}
    User(has_borrowed=[book], favBook=book)

    with pytest.raises(ValueError):
        User(has_borrowed=book, favBook=[book])

    with pytest.raises(ValueError):
        User(has_borrowed=1, favBook=1)


@pytest.mark.parametrize(
    "has_borrowed,fav_book",
    [
        ({"book": {"title": "random"}}, [{"book": {"title": 1}}]),
        ([{"book": {"title": "random"}}], {"book": {"title": 1}}),
    ],
)
def test_referencing_error(has_borrowed, fav_book):
    class Book(GraphQLModel):
        __type__ = "Book"

    class User(GraphQLModel):
        __type__ = "User"

    bindable = PydanticBindable({"Book": Book, "User": User})
    make_executable_schema(
        schema,
        base_scalars_resolvers,
        snake_case_fallback_resolvers,
        bindable,
    )
    with pytest.raises(ValueError):
        User(has_borrowed=has_borrowed, fav_book=fav_book)


@pytest.mark.parametrize(
    "book_type,user_type", [("Unknow", "Unknow"), ("User", "User"), (None, None)]
)
def test_binding_errors(book_type, user_type):
    class Book(GraphQLModel):
        __type__ = book_type

    class User(GraphQLModel):
        __type__ = user_type

    bindable = PydanticBindable({book_type: Book, user_type: User})
    with pytest.raises(PydanticBindError):
        make_executable_schema(
            schema,
            base_scalars_resolvers,
            snake_case_fallback_resolvers,
            bindable,
        )


def test_register_type():
    class Foo(GraphQLModel):
        __type__ = "Foo"

    bindable = PydanticBindable({"Foo": Foo})

    # Remove JSON type
    bindable._type_map.pop("JSON")
    with pytest.raises(PydanticBindError):
        make_executable_schema(
            schema,
            base_scalars_resolvers,
            snake_case_fallback_resolvers,
            bindable,
        )

    # Bring it back through `register` method
    bindable.register_scalar("JSON", dict)
    make_executable_schema(
        schema,
        base_scalars_resolvers,
        snake_case_fallback_resolvers,
        bindable,
    )
