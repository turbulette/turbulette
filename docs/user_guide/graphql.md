All the GraphQL part is handled by [Ariadne](https://ariadnegraphql.org/), a schema-first GraphQL library allowing to write the GraphQL schema using Schema Definition Language ([SDL](https://graphql.org/learn/schema/#type-language)) and bind resolvers to it with minimal code.

Using Ariadne with Turbulette is quite straightforward, all Turbulette does is to define base `query`, `mutation` and `subscription` types for you so you can extend them in the schema.

Refer to [Ariadne documentation](https://ariadnegraphql.org/) for more information.

## Schema

Assuming that we already created our Turbulette project and have an application named `vehicles` inside, let's start with a simple example schema in the `📁 schema` folder:

```graphql
# graphql/schema.graphql

extend type Query {
  cars: [Car]
}


# Types

type Car {
  id: ID!
  model: String!
  brand: String!
  maxSpeed: Float!
  isElectric: Boolean!
}
```

The first thing to note is that we extended the `Query` type. Why? simply because Turbulette already defines it internally. If you forget to `extend` you would get an error like this:

```console
TypeError: There can be only one type named 'Query'
```

The same goes for `Mutation` and `Subscription` types.

## Resolvers

Now that we have some schema defined we have to write the resolver for the `cars` query.

Create a `car.py` in the `resolver` package:

```python hl_lines="22"
# resolvers/car.py

from turbulette import query # ObjectType("Query")

cars = [
    {
        "id": "1234",
        "model": "X",
        "brand": "SuperCars",
        "maxSpeed": 235,
        "isElectric": True
    },
    {
        "id": "4321",
        "model": "tank",
        "brand": "SolidCar",
        "maxSpeed": 145,
        "isElectric": False
    }
]

@query.field("cars")
async def cars_resolver(obj, info):
    return cars
```

The important part here is `#!python @query.field("cars")`: this is how ariadne knows that the `cars_resolver` function is the resolver of the `cars` query.

!!! info

    As you see, we imported `query` from `turbulette` because the `#!python QueryType()` object is already
    defined by Turbulette, hence the need to extend the Query type in the schema.
