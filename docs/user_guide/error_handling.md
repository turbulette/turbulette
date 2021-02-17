# Error handling

In REST APIs, errors are identified with codes (200 ok, 404 not found, 403 unauthorized etc).

In GraphQL, It's a different story because most often you will get a 200 status code
(or 500 for internal server errors). That's by design.

Turbulette format and categorizes errors in meaningful codes to help you understand how the query was carried out.
You can find them under `#!json ["extension"]["errors"]` :

## Examples

```json hl_lines="17 18 19 20"
{
  "data": {
    "books": null
  },
  "errors": [
    {
      "message": "JWT has expired",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": [
        "books"
      ],
      "extensions": {
        "errors": {
          "JWT_EXPIRED": [
            "*"
          ]
        },
```

The `#!json ["extensions"]` object is built with error codes as keys and a list of concerned fields as values. A `#!json "*"` value means that the whole query is concerned.

Take the following example showing an authorization error:

```json hl_lines="20 21 22 23"
{
  "data": {
    "books": {
      "books": [
        {
          "title": "Harry Potter",
          "author": "J.K Rowling",
          "borrowings": null,
        },
        {
          "title": "The Lord of the Rings",
          "author": "J.R.R Tolkien",
          "borrowings": null,
        }
      ]
    }
  },
  "extensions": {
    "errors": {
      "FIELD_NOT_ALLOWED": [
        "borrowings"
      ]
    },
```

Here the response tells us that we are not allowed to access the `"borrowings"` field, but it doesn't means that we can't see the other ones,
hence the "partial" response.

See [here](/reference/error_codes) for a comprehensive list of error codes
