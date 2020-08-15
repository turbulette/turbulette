from calendar import timegm
from datetime import datetime, timedelta
from enum import Enum
from importlib import import_module
from uuid import uuid4

from gino.declarative import Model
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError, decode, encode
from passlib.context import CryptContext

from turbulette.conf import settings

from .exceptions import JSONWebTokenError, JSONWebTokenExpired
from .type import TokenPayload

# Create crypto context
pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

# Dynamically import user model
user_model: Model = getattr(
    import_module(settings.AUTH_USER_MODEL[0]), settings.AUTH_USER_MODEL[1]
)

JWT_REFRESH_TOKEN_TYPE = "refresh"
JWT_ACCESS_TOKEN_TYPE = "access"


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def _jwt_payload(kwarg_name: str, user_id: str) -> dict:
    payload = {kwarg_name: user_id}

    if settings.JWT_AUDIENCE is not None:
        payload["aud"] = settings.JWT_AUDIENCE

    if settings.JWT_ISSUER is not None:
        payload["iss"] = settings.JWT_ISSUER

    return payload


def jwt_payload(user: user_model) -> dict:
    username = user.get_username()

    if hasattr(username, "pk"):
        username = username.pk

    return _jwt_payload(user.USERNAME_FIELD, username)


def jwt_payload_from_id(user_id: str) -> dict:
    return _jwt_payload(user_model.USERNAME_FIELD, user_id)


def get_payload(token: str) -> dict:
    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        raise JSONWebTokenExpired()
    except DecodeError:
        raise JSONWebTokenError("Error decoding signature")
    except InvalidTokenError:
        raise JSONWebTokenError("Invalid token")
    return payload


def encode_jwt(payload: dict, token_type: TokenType) -> str:

    payload["exp"] = (
        datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
        if token_type is TokenType.ACCESS
        else datetime.utcnow() + settings.JWT_REFRESH_EXPIRATION_DELTA
    )

    if (
        settings.JWT_BLACKLIST_ENABLED
        and token_type.value in settings.JWT_BLACKLIST_TOKEN_CHECKS
    ):
        payload["jti"] = str(uuid4())

    payload["type"] = token_type.value
    return encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    ).decode("utf-8")


def decode_jwt(jwt_token: str) -> TokenPayload:
    """Decode JSON web token

    Args:
        auth_token (str): The JSON web token

    Raises:
        JSONWebTokenError: Raised if the signature has expired or if the token is invalid

    Returns:
        int: The user id
    """
    try:
        payload = decode(
            jwt_token,
            settings.SECRET_KEY,
            settings.JWT_VERIFY,
            options={"verify_exp": settings.JWT_VERIFY_EXPIRATION,},
            leeway=settings.JWT_LEEWAY,
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except ExpiredSignatureError:
        raise JSONWebTokenError("Signature expired. Please log in again.")
    except InvalidTokenError:
        raise JSONWebTokenError("Invalid token. Please log in again.")


def get_token_from_user(user: user_model) -> str:
    """A shortcut to get the token directly from a user model instance

    Args:
        user (user_model): GINO model instance of AUTH_USER_MODEL

    Returns:
        str: The JWT token
    """
    return encode_access_token(jwt_payload(user))


def refresh_has_expired(orig_iat) -> bool:
    exp = orig_iat + settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()
    return timegm(datetime.utcnow().utctimetuple()) > exp


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check the password against an existing hash

    Args:
        plain_password (str): Plain password to check
        hashed_password (str): Hashed password to compare to

    Returns:
        bool: ``True`` if the password matched the hash, else ``False``
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get the password hash

    Args:
        password (str): The password to hash

    Returns:
        str: The resulting hash
    """
    return pwd_context.hash(password)


async def login(jwt_token: str) -> user_model:
    """Log a user

    Args:
        auth_token (str): JSON web token

    Raises:
        JSONWebTokenError: Raised if JWT is not found or if the JWT prefix is incorrect

    Returns:
        user_model: The user model instance
    """
    if not jwt_token:
        raise JSONWebTokenError("JWT token not found")
    prefix = jwt_token.split()[0]
    if prefix != settings.JWT_PREFIX:
        raise JSONWebTokenError(
            f"Wrong token prefix in authorization header"
            f"(expecting {settings.JWT_PREFIX} got {prefix})"
        )
    # Get the user's id from the JWT
    payload = decode_jwt(jwt_token.split()[1])
    return await user_model.get_by_username(payload.get(user_model.USERNAME_FIELD))


async def get_user_by_payload(payload):
    username = payload.get(user_model.USERNAME_FIELD)

    if not username:
        raise JSONWebTokenError("Invalid payload")

    user = await user_model.get_by_username(username)

    if user is not None and not getattr(user, "is_active", True):
        raise JSONWebTokenError("User is disabled")
    return user
