"""Provides GraphQL root types.

- `query`
- `mutation`
- `subscription`

And custom scalars :

- `datetime_scalar`
- `date_scalar`
- `json_scalar`

!!! info
    The base app is always loaded, as it should be needed by any other app
    wanting to bind resolvers to the GraphQL schema.
"""

from .resolvers.root_types import (
    query,
    mutation,
    subscription,
    datetime_scalar,
    json_scalar,
)
