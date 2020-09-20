"""Types module.

Define custom Turbulette types
"""

from typing import Awaitable, Dict, List, Callable, Union, Any
from .definition import DatabaseSettings

__all__ = ["DatabaseSettings"]


Principal = List[str]
Claims = Dict[str, Any]
AllowStatement = Dict[str, Dict[str, List[str]]]
Policy = Dict[str, Dict]
PrincipalResolver = Callable[[str, Claims], Awaitable[bool]]
ConditionResolver = Callable[
    [Dict[str, Union[str, List[str]]], Claims], Awaitable[bool]
]
