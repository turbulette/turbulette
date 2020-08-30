from typing import Dict, Any
from ariadne import graphql
from ariadne.types import GraphQLResult, GraphQLSchema


class Tester:
    """Helper class to test GraphQL queries against a schema."""

    def __init__(self, schema: GraphQLSchema):
        self.schema = schema

    async def query(
        self,
        query: str,
        variables: dict = None,
        op_name: str = None,
        headers: dict = None,
        jwt: str = None,
    ) -> GraphQLResult:
        class TestRequest:
            def __init__(self, headers: dict = None, jwt: str = None):
                # Need to import here to make sure that settings are initialized
                from turbulette.conf import settings

                self.headers = {} if not headers else headers
                if jwt:
                    self.headers["authorization"] = f"{settings.JWT_PREFIX} {jwt}"

        return await graphql(
            self.schema,
            data={"query": query, "variables": variables, "operationName": op_name},
            context_value={"request": TestRequest(headers, jwt)},
            debug=True,
        )

    async def assert_query_success(
        self,
        query: str,
        op_name: str,
        variables: dict = None,
        headers: dict = None,
        jwt: str = None,
        op_errors=False,
    ) -> GraphQLResult:
        response = await self.query(query, variables, op_name, headers, jwt)
        self.assert_status_200(response)
        self.assert_no_errors(response)
        assert response[1]["data"][op_name]
        if op_errors:
            assert response[1]["data"][op_name]["errors"]
        else:
            # If no errors, will assert to None
            assert not response[1]["data"][op_name].get("errors")
        return response

    async def assert_query_failed(
        self,
        query: str,
        op_name: str,
        variables: dict = None,
        headers: dict = None,
        jwt: str = None,
    ) -> GraphQLResult:
        response = await self.query(query, variables, op_name, headers, jwt)
        self.assert_status_200(response)
        self.assert_errors(response)
        if response[1]["data"]:
            assert not response[1]["data"][op_name]
        return response

    def assert_status_200(self, response: dict):
        assert response[0]

    def assert_no_errors(self, response: dict):
        assert "errors" not in response[1]

    def assert_errors(self, response: dict):
        assert "errors" in response[1]

    @classmethod
    def assert_data_in_response(cls, response: GraphQLResult, data: Dict[str, Any]):
        """Assert that the response contains the specified key with the corresponding values.

        Args:
            response (GraphQLResult): Response to check
            data (Dict[str, Any]): Data that should be present in query response
        """
        for key, value in data.items():
            if key in response:
                assert response[key] == value
