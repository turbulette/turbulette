# Custom scalars

## DateTime

DateTime scalar, follows [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601).

It parses ISO 8601 or [RFC 3339](https://tools.ietf.org/html/rfc3339)
formatted strings into Python `datetime` objects.

Serializing is done using the
[isoformat()](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)
method, returning an ISO 8601 representation of `datetime` objects.

## Date

Date scalar, follows ISO 8601.

Parses and serializes ISO 8601 formatted dates (`YYY-MM-DD`).

## JSON

This scalar parses JSON strings contained in a `String` GraphQL field,
and load them as Python objects.
