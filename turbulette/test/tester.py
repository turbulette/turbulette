from ariadne import graphql
from ariadne.types import GraphQLResult, GraphQLSchema


class Tester:
    """Helper class to test GraphQL queries against a schema
    """

    def __init__(self, schema: GraphQLSchema):
        self.schema = schema

    async def query(
        self, query: str, variables: dict = None, op_name: str = None
    ) -> GraphQLResult:
        return await graphql(
            self.schema,
            data={"query": query, "variables": variables, "operationName": op_name},
        )

    async def assert_query_success(
        self, query: str, variables: dict = None, op_name: str = None
    ) -> GraphQLResult:
        response = await self.query(query, variables, op_name)
        self.assert_status_200(response)
        self.assert_no_errors(response)
        return response

    async def assert_query_failed(
        self, query: str, variables: dict = None, op_name: str = None
    ) -> GraphQLResult:
        response = await self.query(query, variables, op_name)
        self.assert_status_200(response)
        self.assert_errors(response)
        return response

    def assert_status_200(self, response: dict):
        assert response[0]

    def assert_no_errors(self, response: dict):
        assert "errors" not in response[1]

    def assert_errors(self, response: dict):
        assert "errors" in response[1]
