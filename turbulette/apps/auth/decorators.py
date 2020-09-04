from datetime import datetime
from typing import Any, Callable
from turbulette.core.errors import PermissionDenied
from .core import TokenType, decode_jwt, process_jwt_header, settings
from .permissions import has_scope
from .exceptions import JWTInvalidTokenType, JWTNotFresh


def scope_required(permissions: list, is_staff=False):
    """Scope decorator.

    Log a user and check if it has the required permissions
    before executing the wrapped function

    If the user successfully has been successfully logged in,
    the user model instance is added to the context dictionary
    with the key ``user``
    """

    def wrap(func: Callable[..., Any]):
        @access_token_required
        async def wrapped_func(obj, info, claims, **kwargs):
            authorized = await has_scope(claims["sub"], permissions, is_staff)
            if authorized:
                return await func(obj, info, claims, **kwargs)
            return PermissionDenied().dict()

        return wrapped_func

    return wrap


def access_token_required(func: Callable[..., Any]):
    """Access token decorator.

    Decorator that require a jwt access token
    before executing the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``
    """

    @_jwt_required(TokenType.ACCESS)
    async def wrapper(obj, info, claims, **kwargs):
        return await func(obj, info, claims, **kwargs)

    return wrapper


def fresh_token_required(func: Callable[..., Any]):
    """Fresh token decorator.

    Decorator that require a fresh jwt access token
    before executing the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``

    The "freshness" is determined by the `JWT_FRESH_DELTA` timedelta setting
    """

    @_jwt_required(TokenType.ACCESS)
    async def wrapper(obj, info, claims, **kwargs):
        if (
            datetime.utcnow() - datetime.utcfromtimestamp(claims["iat"])
        ) > settings.JWT_FRESH_DELTA:
            raise JWTNotFresh()
        return await func(obj, info, claims, **kwargs)

    return wrapper


def refresh_token_required(func: Callable[..., Any]):
    """Refresh token decorator.

    Decorator that require a jwt refresh token
    before executing the wrapped function

    If the user successfully has been successfully
    logged in, the user model instance is added to
    the context dictionary with the key ``user``
    """

    @_jwt_required(TokenType.REFRESH)
    async def wrapper(obj, info, claims, **kwargs):
        return await func(obj, info, claims, **kwargs)

    return wrapper


def _jwt_required(token_type: TokenType):
    """Base decorator for requiring JWT."""

    def wrap(func: Callable[..., Any]):
        async def wrapped_func(obj, info, **kwargs):
            jwt = process_jwt_header(info.context["request"].headers["authorization"])
            claims = decode_jwt(jwt)[1]
            if TokenType(claims["type"]) is not token_type:
                raise JWTInvalidTokenType(
                    f"The provided JWT is not a {token_type.value} token"
                )
            return await func(obj, info, claims, **kwargs)

        return wrapped_func

    return wrap
