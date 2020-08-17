from typing import Any, Callable, Tuple, TypeVar

from turbulette.core.errors import PermissionDenied

from .core import TokenType, decode_jwt, process_jwt_header
from .permissions import has_scope

F = TypeVar("F", bound=Callable[..., Any])


def scope_required(permissions: list, is_staff=False) -> F:
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
        @access_token_required
        async def wrapped_func(obj, info, claims, **kwargs):
            authorized = await has_scope(claims["sub"], permissions, is_staff)
            if authorized:
                return await func(obj, info, claims, **kwargs)
            return PermissionDenied().dict()

        return wrapped_func

    return wrap


def access_token_required(func: F) -> F:
    """Decorator that require a jwt access token
        before executing the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``

    Args:
        func (FunctionType): Async function to wrap

    Returns:
        FunctionType: The wrapped resolver
    """

    @_jwt_required(TokenType.ACCESS)
    async def wrapper(obj, info, claims, **kwargs):
        return await func(obj, info, claims, **kwargs)

    return wrapper


def refresh_token_required(func: F) -> F:
    """Decorator that require a jwt refresh token
        before executing the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``

    Args:
        func (FunctionType): Async function to wrap

    Returns:
        FunctionType: The wrapped resolver
    """

    @_jwt_required(TokenType.REFRESH)
    async def wrapper(obj, info, claims, **kwargs):
        return await func(obj, info, claims, **kwargs)

    return wrapper


def _jwt_required(token_type: TokenType) -> Tuple:
    def wrap(func: F) -> F:
        async def wrapped_func(obj, info, **kwargs):
            jwt = process_jwt_header(info.context["request"].headers["authorization"])
            claims = decode_jwt(jwt)[1]
            if TokenType(claims["type"]) is not token_type:
                raise PermissionError(
                    f"The provided token is not a {token_type.value} token"
                )
            return await func(obj, info, claims, **kwargs)

        return wrapped_func

    return wrap
