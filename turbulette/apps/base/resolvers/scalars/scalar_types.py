import json
from ariadne import ScalarType

datetime_scalar = ScalarType("DateTime")
json_scalar = ScalarType("JSON")

base_scalars_resolvers = [datetime_scalar, json_scalar]

@datetime_scalar.serializer
def serialize_datetime(value):
    return value.isoformat()

@json_scalar.value_parser
def parse_json(value):
    if not value:
        return {}
    return json.loads(value)
