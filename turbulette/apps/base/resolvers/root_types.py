import json
from datetime import datetime
from typing import Any

import ciso8601
from ariadne import MutationType, QueryType, ScalarType

query = QueryType()
mutation = MutationType()

# Custom scalars
datetime_scalar = ScalarType("DateTime")
date_scalar = ScalarType("Date")
json_scalar = ScalarType("JSON")

base_scalars_resolvers = [datetime_scalar, date_scalar, json_scalar]


@datetime_scalar.value_parser
def parse_datetime(value: str) -> datetime:
    return ciso8601.parse_datetime(value)


@datetime_scalar.serializer
def serialize_datetime(value: Any) -> str:
    return value.isoformat()


@date_scalar.serializer
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
