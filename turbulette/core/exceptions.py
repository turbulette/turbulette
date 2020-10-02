class NotReady(Exception):
    pass


class SchemaError(Exception):
    """The GraphQL schema is improperly configured."""
