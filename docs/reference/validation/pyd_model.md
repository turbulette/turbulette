# Pydantic

Turbulette has an [Ariadne bindable](https://ariadnegraphql.org/docs/bindables)
that can automatically add fields and annotations to a pydantic model from a given GraphQL type.

For this to work, Pydantic models must subclass `GraphQLModel` and define a `__type__` class attribute
that indicates the corresponding GraphQL type:

```graphql
type User {
    username: String!
    email: String!
    age: Int
}
```

```python
from turbulette.validation import GraphQLModel

class User(GraphQLModel):
    __type__ = "User"
```

During schema binding, attributes `username`, `email` and `age` will be added to the `User` model
with proper Python annotations.

All GraphQL scalars will be converted to their Python equivalent :

| GraphQL Scalar | Python annotation |
| -------------- | ----------------- |
| Int            | `int`             |
| Float          | `float`           |
| String         | `str`             |
| Boolean        | `bool`            |
| ID             | `Union[str, int]` |


The same goes for wrapping types :

| GraphQL Wrapping type | Python annotation                                                                  |
| --------------------- | ---------------------------------------------------------------------------------- |
| List                  | `List`                                                                             |
| Non-Null              | Every nullable fields have `None` as default value, non-nullable ones are required |

For non scalar fields (i.e: other GraphQL types), the bindable will look
for an existing `GraphQLModel` that describes it. If it can't found it,
a `PydanticBindError` will be raised.

::: turbulette.validation.pyd_model
    selection:
        filters:
            - "!^(PydanticBindable|GraphQLMetaclass|add_fields)$"

::: turbulette.validation.exceptions
