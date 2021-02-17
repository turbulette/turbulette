Turbulette integrates with [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation,
and can generates pydantic models directly from the GraphQL schema.

One of the most useful usages of Pydantic in an API is validating input data. As our API is typed
thanks to GraphQL we already *know* what will be this input data, or in other words, we have the
necessary information to generate Pydantic models that will validate input data.

## GraphQLModel

Take the following GraphQL schema:

```graphql
extend type Mutation {
    registerCard(input: CreditCardInput!): SuccessPayload!
}

type SuccessPayload {
  success: Boolean
  errors: [String]
}

input CreditCardInput {
    number: String!
    cvc: Int!
    expiry: Date!
    name: String!
}
```

!!! tip
    Note the `errors` fields in the `SuccessPayload`. This where validation error messages will appear if validation fails.
    If you forget it, you won't see any error messages in you GraphQL response

To start, create a `📄 pyd_models.py` in your app directory: this is where Turbulette will look
for pydantic models that needs to binded to the schema:

```python
# pyd_models.py

from turbulette.validation import GraphQLModel
from pydantic import PaymentCardNumber


class CreditCard(GraphQLModel):
    class GraphQL:
        gql_type = "CreditCardInput"
```

`GraphQLModel` is derived from the base Pydantic `BaseModel` class with the ability to
dynamically add fields to the existing class. Turbulette use it to add fields inferred
from the GraphQL specified by `gql_type` attribute.

Right now, our `CreditCard` pydantic model is strictly equivalent to this pure pydantic model:

```python
# pyd_models.py

from datetime import datetime
from pydantic import BaseModel

class CreditCard(BaseModel):
    number: str
    cvc: int
    expiration: datetime
    name: str
```

The expiration field has the type `Date` in our GraphQL schema. This is a custom scalar provided by Turbulette,
and is mapped to a Python `Datetime` object in pydantic models.

## Validate decorator

On the resolver side, Turbulette has a decorator that can be used to easily validate data using
a pydantic model:

```python hl_lines="4 8 9"
# resolvers/card.py

from ..pyd_models import CarInputModel
from turbulette.validation import validate
from turbulette import mutation

@mutation.field("registerCard")
@validate(CardInput)
async def add_card(obj, info, **kwargs):
    return {
        "success": True
    }
```

When using the `#!python @validate()`, you will find validated data in `!#python kwargs["_val_data"]` if the pydantic validation succeed.

## Validators

At this point, the validation doesn't add much on top of GraphQL typing (just the date parsing for expiration field),
so let's add some pydantic validators:

```python
# pyd_models.py

from turbulette.validation import GraphQLModel, validator

class CreditCard(GraphQLModel):
    class GraphQL:
        gql_type = "CreditCardInput"

    @validator("cvc")
    def check_cvc(val) -> None:
        if len(str(val)) != 3:
            raise ValueError("cvc number must be composed of 3 digits")

    @validator("expiry")
    def check_expiration(val: DateTime) -> None:
        if val <= datetime.now():
            raise ValueError("Expiry date has passed")
```

!!! tip
    For those who have already used Pydantic, you probably know about the `#!python @validator` decorator used to add custom validation rules on fields.

    But here, we use a `#!python @validator` imported from `turbulette.validation`, why?

    They're almost identical. Turbulette's validator is just a shortcut to the Pydantic one with `check_fields=False` as a default, instead of `True`,
    because we use an inherited `BaseModel`. The above snippet would correctly work if we used Pydantic's validator and explicitly set `#!python @validator("expiration", check_fields=False)`.

If you try entering wrong expiry date or cvc, you will get validation errors has expected:

```graphql
mutation {
  registerCard(input: {
    number: "4000000000000002"
    cvc: 111111111 # wrong
    expiry: "1875-05-04" # wrong
    name: "John Doe"
  }) {
    errors
    success
  }
}
```

Gives us:

```graphql
{
  "data": {
    "registerCard": {
      "errors": [
        "cvc: cvc must be composed of 3 digits",
        "expiry: Expiry date has passed"
      ],
      "success": null
    }
  }
}
```

## Override fields typing

As we register credit cards, we also want to validate the card number. Fortunately, pydantic
offers some custom types, including a `PaymentCardNumber` one.

So what we want is to type the `number` as `PaymentCardNumber` instead of `str`. We can do this by using
the `fields` attributes in the `GraphQL` inner class:

```python hl_lines="4 5 6"
# pyd_models.py

class CardInput(GraphQLModel):
    class GraphQL:
        gql_type = "CreditCardInput"
        fields = {
            "number": PaymentCardNumber
        }

    @validator("cvc")
    def check_cvc(val) -> None:
        if len(str(val)) != 3:
            raise ValueError("cvc must be composed of 3 digits")

    @validator("expiry")
    def check_expiration(val: DateTime) -> None:
        if val <= datetime.now():
            raise ValueError("Expiry date has passed")
```

The equivalent typing using pydantic's BaseModel is:

```python hl_lines="8"
# pyd_models.py

from datetime import datetime
from pydantic import BaseModel
from pydantic.types import PaymentCardNumber

class CreditCard(BaseModel):
    number: PaymentCardNumber
    cvc: int
    expiration: datetime
    name: str
```
