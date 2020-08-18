from tests.turbulette_tests.queries import mutation_create_book, query_book
import pytest
from datetime import datetime

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
            "publicationDate": datetime(year=1996, month=8, day=1),
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
