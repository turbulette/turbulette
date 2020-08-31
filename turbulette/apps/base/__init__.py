"""Provides root query, mutation and scalar objects.

The base app is always loaded, as it should be needed by any other app
wanting to bind a resolver to the GraphQL schema
"""

from .resolvers.root_types import query, mutation, datetime_scalar, json_scalar
