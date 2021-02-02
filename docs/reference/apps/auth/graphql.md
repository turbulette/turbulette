GraphQL schema exposed by the auth app

## Types

``` gql
type JsonWebToken {
  accessToken: String
  refreshToken: String
  errors: [String]
}

type AccessToken {
  accessToken: String
  errors: [String]
}
```

## Queries

``` gql
getJWT(username: String!, password: String!): JsonWebToken
refreshJWT: AccessToken
```

## Directives

``` gql
directive @policy on FIELD_DEFINITION
directive @access_token_required on FIELD_DEFINITION
directive @fresh_token_required on FIELD_DEFINITION
```
