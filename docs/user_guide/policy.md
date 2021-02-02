# Policy module

## Introduction

Turbulette auth application provides a policy based access control
([PBAC](https://en.wikipedia.org/wiki/Attribute-based_access_control)) allowing you
to manage authorization in a granular way, through a declarative syntax, in a dedicated JSON configuration file.

A policy defines *who* can access *what* under *which* conditions.

They are evaluated before
query execution if the GraphQL field has the `#!graphql @policy` directive:

```graphql
extend type Query {
    buyPremiumBook(bookId: ID): Book! @policy
    buyBook(bookId: ID): Book!
}
```

Only query or mutations with the `@policy` directive will be considered for policies evaluation.
Others are unrestricted by default.

## Policy

To add policies, create a `policies.json` in the project directory. This file will contains
the *policy schema*, that is, the list of all policies (you can add as many as you want) defining your authorization model.
A policy is a JSON object holding needed information to evaluate whether or not the user is authorized to access the asked resource:
principals, conditions and resources that are allowed or denied.

!!! info
    Policy evaluation follow the principle of *least privilege*: access is granted if *any* policy allows it, and *no* policy denies it

### principal

*Who* is concerned by the policy. It's an array of identifiers, each matching a subset of users based on role, permission, staff member etc. A principal string is formatted as follows:

```#!json "<identifier>:<value>"```

e.g: ```#!json "perm:read_premium_articles"``` match user with `read_premium_articles` permission

Turbulette defines four principal identifiers:

- `authenticated`: Math all authenticated user i.e: any user with a valid JWT

- `perm:<permission>`: Match all users with the given permission

- `role:<role>`: Match all users belonging to this role

- `staff`: Match staff user only

### conditions

Optional. defines *which* conditions must be met in order to apply the policy. Included conditions are:

- `claim`

    Must be a JSON object containing a `name` key indicating the
    name of the claim to look for, an `includes` array that sppecifies
    values that the claim must includes:

    ```json
      "claim": {
        "name": "scopes",
        "includes": ["_staff"]
      }
    ```

- `is_claim_present`

    The name of a JWT claim that must be present:

    ```json
    "is_claim_present": "iss"
    ```

### Allow and deny access

- `allow`

    What query of specific fields are allowed if the policy is applied

- `deny`

    What query or specific fields are denied if the policy is applied

Let's take a look at the following policy:

```json
  {
    "principal": ["staff"],
    "conditions": {
      "is_claim_present": "iss",
      "claim": {
        "name": "scopes",
        "includes": ["_staff"]
      }
    },
    "allow": {
      "mutation": {
        "fields": ["addBook"]
      }
    }
  },
```

According to the `principal`, only staff user are concerned about this policy and there are two
conditions that must be met for it to be applied:

- The `iss` claim must be present
- The `scopes` claim must includes `#!json "_staff"` value

Then, if the user user is a staff member and the above conditions are met,
the `addBook` mutation is allowed.

A resource is *what* the user is actually asking for. In GraphQL, the resource is clearly described in the query:

```graphql
mutation {
  prescribeDrug {
    name
    dose
    frequency
  }
}
```

Let's write a policy where only user with the `doctor` role are allowed to prescribe drugs:

```json
  {
    "principal": ["role:doctor"],
    "allow": {
      "mutation": {
        "fields": ["prescribeDrug"]
      }
    }
  }
```

The resource on which the policy is applied is the whole `prescribeDrug` mutation,
anyone outside `doctor` users is not authorized to execute this mutation.

Note that we used `fields` array to restrict the mutation, because
both `Query` and `Mutation` are (almost) no different than any other GraphQL types,
except that they reference user queries and mutations. So it's totally valid to
say that the above policy authorize access to the `prescribeDrug` *field* of the `Mutation`
*type*

This leads to the following question:

Is it possible to restrict access to specific fields of *other* GraphQL type? (Yes!)

```graphql
query {
  healthRecord {
    name
    age
    phone
    weight
  }
}
```

We want the `weight` to be restricted to only users with `medical:read` permission,
and other fields to be freely accessible. If we change the previous example a little, we get:

```json hl_lines="2 4 5"
  {
    "principal": ["perm:medical:read"],
    "allow": {
      "healthRecord": {
        "fields": ["weight"]
      }
    }
  }
```

Now, whatever the query, if the return type is, or include a `healthRecord` GraphQL type the policy will
be applied so `weight` field will *never* appears for users who don't have `medical:read` permission.

## Add policy resolvers

The policy system is extendable so you can add your own
conditions and principals easily. In the same way you bind resolvers
to your GraphQL queries, you'd write resolvers for policy conditions and principals,
and bind them to the policy schema:

Every condition/principal resolver take three parameters:

- `val`: The value associated to the condition/principal key
- `claims`: JWT claims of the token sent in the request
- `info`: GraphQL execution context

### Examples

#### Condition

```python
from datetime import datetime
from turbulette.apps.auth import policy

@policy.condition("is_new_year_day")
async def new_year(val, claims: Claims, info: GraphQLResolveInfo) -> bool:
    """This condition ensure that the current day is January the 1st of the year."""
    return datetime.today().day == 1 and datetime.today().month == 1
```


The `policy` imported from `turbulette.apps.auth` is a `PolicyType` instance
responsible for evaluating policies. It also serves as a registry for policy
conditions and principals resolvers, that are added using the `#!python @policy.condition()`
decorator. The only param needed to be passed to it is the condition name that you will
use on the policy schema:

```json hl_lines="4"
{
  "principal": ["authenticated"],
  "conditions": {
    "is_new_year": ""
  },
  "allow": {
    "query": {
      "fields": ["newYearQuery"]
    }
  }
}
```

In this case the `is_new_year` condition does not need any additional information so
we set it to an empty string.

#### Principal

Adding principal resolvers follow the same principles:

```python
from turbulette.apps.auth import policy

@policy.principal("name_start_with")
async def name_resolver(val, claims: Claims, info: GraphQLResolveInfo) -> bool:
    """Check that the username start with a given letter."""
    return claims["sub"].startswith(val)
```

Usage in the policy schema:

```json
{
  "principal": ["name_start_with:d"],
  "allow": {
    "query": {
      "fields": ["nameInfos"]
    }
  }
}
```

Only user with username starting with `"d"` will be authorized to perform the `nameInfos` query.
