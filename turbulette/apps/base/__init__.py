"""Provides root query, mutation and scalar objects.

The base app is always loaded, as it should be needed by any other app
wanting to bind a resolver to the GraphQL schema
"""

from .resolvers.mutations.mutation_type import mutation  # noqa
from .resolvers.queries.query_type import query  # noqa
from .resolvers.scalars.scalar_types import datetime_scalar, json_scalar  # noqa
