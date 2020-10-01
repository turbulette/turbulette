"""Types module.

Define custom Turbulette types
"""

from typing import Any, Awaitable, Callable, Dict, List, Union

from ariadne.types import GraphQLResolveInfo

from .definition import DatabaseSettings

__all__ = ["DatabaseSettings"]


Principal = List[str]
Claims = Dict[str, Any]
AllowStatement = Dict[str, Dict[str, List[str]]]
Policy = Dict[str, Dict]
PrincipalResolver = Callable[[str, Claims, GraphQLResolveInfo], Awaitable[bool]]
ConditionResolver = Callable[
    [Dict[str, Union[str, List[str]]], Claims, GraphQLResolveInfo], Awaitable[bool]
]
