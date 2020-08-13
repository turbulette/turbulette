from typing import Callable, Any, TypeVar
from turbulette.core.errors import BaseError, PermissionDenied
from .exceptions import JSONWebTokenError
from .core import login
from .permissions import has_permission

Func = TypeVar("F", bound=Callable[..., Any])


def login_required(func: Func) -> Func:
    """Decorator that log a user before executing
        the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``

    Args:
        func (FunctionType): Async function to wrap

    Returns:
        FunctionType: The wrapped resolver
    """

    async def wrapper(obj, info, **kwargs):
        try:
            info.context["user"] = await login(info.context["request"].headers["authorization"])
            return await func(obj, info, **kwargs)
        except JSONWebTokenError as exception:
            return BaseError(exception.message).dict()

    return wrapper


def staff_member_required(func: Func) -> Func:
    """Decorator that log a user and check
        if it's a staff member before executing
        the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``

    Args:
        func (FunctionType): Async function to wrap

    Returns:
        FunctionType: The wrapped resolver
    """

    async def wrapper(obj, info, **kwargs):
        try:
            user = await login(info.context["request"].headers["authorization"])
            if user.is_staff:
                info.context["user"] = user
                return await func(obj, info, **kwargs)
            return PermissionDenied().dict()
        except JSONWebTokenError as exception:
            return BaseError(exception.message).dict()

    return wrapper


def permission_required(permissions: list) -> Func:
    """Decorator that log a user and check if it
        has the required permissions
        before executing the wrapped function

    If the user successfully has been successfully logged in,
    the user model instance is added to the context dictionary
    with the key ``user``

    Args:
        func (FunctionType): Async function to wrap

    Returns:
        FunctionType: The wrapped resolver
    """

    def wrap(func):
        async def wrapped_func(obj, info, **kwargs):
            authorized = False
            try:
                user = await login(info.context["request"].headers["authorization"])
            except JSONWebTokenError as exception:
                return BaseError(exception.message).dict()
            if permissions:
                if user.permission_group:
                    authorized = await has_permission(user, permissions)
            if authorized:
                info.context["user"] = user
                return await func(obj, info, **kwargs)
            return PermissionDenied().dict()

        return wrapped_func

    return wrap
