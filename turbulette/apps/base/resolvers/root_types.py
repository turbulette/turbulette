import json
from datetime import datetime
from typing import Any, Callable

import ciso8601
from ariadne import MutationType, QueryType, ScalarType
from turbulette import conf

query = QueryType()
mutation = MutationType()

# Custom scalars
datetime_scalar = ScalarType("DateTime")
date_scalar = ScalarType("Date")
json_scalar = ScalarType("JSON")

base_scalars_resolvers = [datetime_scalar, date_scalar, json_scalar]


def _extract_value(func: Callable[[Any], str]) -> Callable[[Any], str]:
    """If `value` is a dict, return the first item.
    When a query return a custom scalar, it is wrapped in a dict
    so we have to extract it before the serialization.
    """

    def wrapped(value: Any):
        if isinstance(value, dict) and conf.settings.ERROR_FIELD not in value:
            value = value[next(iter(value))]
        return func(value)

    return wrapped


@datetime_scalar.value_parser
def parse_datetime(value: str) -> datetime:
    return ciso8601.parse_datetime(value)


@datetime_scalar.serializer
@_extract_value
def serialize_datetime(value: Any) -> str:
    return value.isoformat()


@date_scalar.serializer
@_extract_value
def serialize_date(value: Any) -> str:
    return value.strftime("%Y-%m-%d")


@date_scalar.value_parser
def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


@json_scalar.value_parser
def parse_json(value: str) -> Any:
    if not value:
        return {}
    return json.loads(value)
