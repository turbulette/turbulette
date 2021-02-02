## Policy conditions

A policy can define conditions under which queries or fields
are allowed.

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

## Policy principals

The `#!json "principal"` array specifies a subset of user who are concerned by the policy.

- `authenticated`

    Math all authenticated user i.e: any user with a valid JWT

- `perm:<permission>`

    Match all users with the given permission

- `role:<role>`

    Match all users belonging to this role

- `staff`

    Match staff user only

Example:

`#!json "principal": ["perm:book:borrow", "role:customer"]`

Match users with `#!json "book:borrow"` permission and `#!json "customer"` role.


::: turbulette.apps.auth.policy.base
    selection:
        members:
            - authorized

::: turbulette.apps.auth.policy.policy
    selection:
        filters:
            - "!^_"
            - "!^apply$"
