class PydanticBindError(Exception):
    """Raised if Turbulette fails to bind GraphQL pydantic models.

    Common causes are:

    - The pydantic model does not defines a `__type__` attribute.
    - The GraphQL type defined by `__type__` does not exists.
    - The GraphQL type exists, but one of its fields refers to a GraphQL type that does not exist.
    """
