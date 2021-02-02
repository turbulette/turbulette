# Error handling

In REST APIs, errors are identified with codes (200 ok, 404 not found, 403 unauthorized etc).

In GraphQL, It's a different story because most often you will get a 200 status code
(or 500 for internal server errors). That's by design.

Turbulette categorizes errors in meaningful codes, that can be found in two places, depending on how the query was carried out:

- **Something went wrong, the query couldn't be executed:**

    The GraphQL `errors` array will show up, and you will not get
    your expected `data` key (in which you would find the query response). In this case, Turbulette will place the error code in
    `#!json ["errors"]["extension"]["code"]`.

- **The query returned some data, but still, something went wrong:**

    This is a less common case, when something went wrong but
    didn't prevent the query to return a result. For example this is the case
    when some of the query fields are not allowed: It does not means that
    *all* of the fields are forbidden, so there is no reason why allowed
    fields cannot be returned.

    In this case, error codes will appears in `#!json ["extension"]["policy"]`.

See [here](/reference/error_codes) for a comprehensive list of error codes
