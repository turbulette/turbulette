from typing import Callable, Any, Tuple, TypeVar
from turbulette.core.errors import BaseError, PermissionDenied
from .exceptions import UserDoesNotExists, InvalidJWTSignatureError
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
            user = await login(info.context["request"].headers["authorization"])
            return await func(obj, info, user, **kwargs)
        except InvalidJWTSignatureError as error:
            return BaseError(error.message).dict()
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

    @login_required
    async def wrapper(obj, info, user, **kwargs):
        if user.is_staff:
            staff_user = user
            return await func(obj, info, staff_user, **kwargs)
        return PermissionDenied().dict()

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
        @login_required
        async def wrapped_func(obj, info, user, **kwargs):
            authorized = False
            if permissions:
                authorized = await has_permission(user, permissions)
            if authorized:
                info.context["user"] = user
                return await func(obj, info, user, **kwargs)
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
            token = info.context["request"].headers["authorization"].split()[1]
            try:
                claims = decode_jwt(token)[1]
                if TokenType(claims["type"]) is not token_type:
                    raise PermissionError(
                        f"The provided token is not a {token_type.value} token"
                    )
                return await func(obj, info, claims, **kwargs)
            except InvalidJWTSignatureError as error:
                return BaseError(error.message).dict()

        return wrapped_func

    return wrap
