from datetime import datetime

import pytest
from ariadne import (
    MutationType,
    QueryType,
    gql,
    graphql,
    make_executable_schema,
    snake_case_fallback_resolvers,
)

from tests.turbulette_tests.queries import mutation_create_book, query_book
from turbulette.apps.base.resolvers.root_types import base_scalars_resolvers

pytestmark = pytest.mark.asyncio


profile_str = """
    {
        "genre": ["epic fantasy", "political novel"],
        "awards": ["Locus Award for Best Fantasy Novel"]
    }
"""

profile_obj = {
    "genre": ["epic fantasy", "political novel"],
    "awards": ["Locus Award for Best Fantasy Novel"],
}

profile_empty = {"genre": None, "awards": None}


@pytest.mark.parametrize(
    "profile,profile_output",
    [(profile_str, profile_obj), ("", profile_empty), (None, None)],
)
async def test_book(tester, profile, profile_output):
    response = await tester.assert_query_success(
        query=mutation_create_book,
        variables={
            "title": "A Game of Thrones",
            "author": "George R. R. Martin",
            "publicationDate": datetime(year=1996, month=8, day=1).isoformat(),
            "profile": profile,
        },
        op_name="createBook",
    )

    assert response[1]["data"]["createBook"]["book"]["title"]
    assert response[1]["data"]["createBook"]["book"]["author"]
    assert response[1]["data"]["createBook"]["book"]["publicationDate"]
    assert response[1]["data"]["createBook"]["book"]["profile"] == profile_output

    response = await tester.assert_query_success(
        query=query_book,
        variables={"id": response[1]["data"]["createBook"]["book"]["id"]},
        op_name="book",
    )

    assert response[1]["data"]["book"]["book"]["title"]
    assert response[1]["data"]["book"]["book"]["author"]
    assert response[1]["data"]["book"]["book"]["publicationDate"]
    assert response[1]["data"]["book"]["book"]["profile"] == profile_output


async def test_date():
    schema = gql(
        """
        scalar Date
        scalar DateTime
        scalar JSON

        type Query {
            event: Event!
        }
        type Mutation {
            createEvent(date: Date!): Boolean!
        }
        type Event {
            date: Date!
        }
    """
    )

    query_event = """
    query {
        event {
            date
        }
    }
    """

    mutation_event = """
    mutation createEvent($date: Date!) {
        createEvent(date: $date)
    }
    """

    query_type = QueryType()
    mutation_type = MutationType()

    @mutation_type.field("createEvent")
    async def createEvent(obj, parent, **kwargs):
        return True

    @query_type.field("event")
    async def event(obj, parent, **kwargs):
        return {"date": datetime.now()}

    schema = make_executable_schema(
        schema, query_type, base_scalars_resolvers, snake_case_fallback_resolvers
    )

    await graphql(schema=schema, data={"query": query_event})
    await graphql(
        schema=schema,
        data={
            "query": mutation_event,
            "variables": {
                "date": "1789-07-07T12:00:00+02:00"
            },  # ISO 8601 datetime string
        },
    )
