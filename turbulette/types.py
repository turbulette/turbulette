"""Types module.

Define custom Turbulette types
"""

from typing import Any, Awaitable, Callable, Dict, List, Sequence, Union

from ariadne.types import GraphQLResolveInfo
from starlette.config import Config
from starlette.requests import Request


Principal = List[str]
Claims = Dict[str, Any]
AllowStatement = Dict[str, Dict[str, List[str]]]
Policy = Dict[str, Dict]
PrincipalResolver = Callable[[str, Claims, GraphQLResolveInfo], Awaitable[bool]]
ConditionResolver = Callable[
    [Dict[str, Union[str, List[str]]], Claims, GraphQLResolveInfo], Awaitable[bool]
]
DatabaseSettings = Dict[str, Config]
LoaderFunction = Callable[[Sequence[Any]], Awaitable[Sequence[Any]]]

GraphQLContext = Dict[str, Any]
GraphQLContextAction = Callable[[Request], Awaitable[GraphQLContext]]
GraphQLContextFilter = Callable[
    [GraphQLContextAction, Request], Awaitable[GraphQLContext]
]
DatabaseConnectionParams = Dict[str, Config]
