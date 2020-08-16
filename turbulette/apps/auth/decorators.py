from typing import Callable, Any, Tuple, TypeVar
from turbulette.core.errors import BaseError, PermissionDenied
from .exceptions import JSONWebTokenError, UserDoesNotExists
from .core import TokenType, decode_jwt, login
from .permissions import has_permission


F = TypeVar("F", bound=Callable[..., Any])


def login_required(func: F) -> F:
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
            user = await login(
                info.context["request"].headers["authorization"]
            )
            return await func(obj, info, user, **kwargs)
        except JSONWebTokenError as exception:
            return BaseError(exception.message).dict()
        except UserDoesNotExists:
            return BaseError("User does not exists").dict()

    return wrapper


def staff_member_required(func: F) -> F:
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


def permission_required(permissions: list) -> F:
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

    async def wrapper(obj, info, **kwargs):
        try:
            jwt_claims = _jwt_required(info, TokenType.ACCESS)
            return await func(obj, info, jwt_claims, **kwargs)
        except JSONWebTokenError as error:
            return BaseError(error.message).dict()

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

    async def wrapper(obj, info, **kwargs):
        try:
            jwt_claims = _jwt_required(info, TokenType.REFRESH)
            return await func(obj, info, jwt_claims, **kwargs)
        except JSONWebTokenError as error:
            return BaseError(error.message).dict()

    return wrapper


def _jwt_required(info, token_type: TokenType) -> Tuple:
    token = info.context["request"].headers["authorization"].split()[1]
    claims = decode_jwt(token)[1]
    if TokenType(claims["type"]) is not token_type:
        raise PermissionError(
            f"The provided token is not a {token_type.value} token"
        )
    return claims
