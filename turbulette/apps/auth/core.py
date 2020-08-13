from calendar import timegm
from datetime import datetime, timedelta
from importlib import import_module
from gino.declarative import Model
from jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
    decode,
    encode,
    DecodeError,
)
from passlib.context import CryptContext

from turbulette.conf import settings

from .exceptions import JSONWebTokenError, JSONWebTokenExpired


jwt_settings = settings.GRAPHQL_JWT

# Create crypto context
pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

# Dynamically import user model
user_model: Model = getattr(
    import_module(settings.AUTH_USER_MODEL[0]), settings.AUTH_USER_MODEL[1]
)


def jwt_payload(user: user_model, context=None) -> dict:
    username = user.get_username()

    if hasattr(username, "pk"):
        username = username.pk

    payload = {
        user.USERNAME_FIELD: username,
        "exp": datetime.utcnow() + jwt_settings["JWT_EXPIRATION_DELTA"],
    }

    if jwt_settings["JWT_ALLOW_REFRESH"]:
        payload["origIat"] = timegm(datetime.utcnow().utctimetuple())

    if jwt_settings["JWT_AUDIENCE"] is not None:
        payload["aud"] = jwt_settings["JWT_AUDIENCE"]

    if jwt_settings["JWT_ISSUER"] is not None:
        payload["iss"] = jwt_settings["JWT_ISSUER"]

    return payload


def get_payload(token: str, context=None) -> dict:
    try:
        payload = decode_jwt(token)
    except ExpiredSignatureError:
        raise JSONWebTokenExpired()
    except DecodeError:
        raise JSONWebTokenError("Error decoding signature")
    except InvalidTokenError:
        raise JSONWebTokenError("Invalid token")
    return payload


def encode_jwt(user: user_model) -> str:
    """Encode a JSON web token

    Args:
        user (user_model): user_model instance

    Returns:
        str: The JSON web token
    """

    return encode(
        jwt_payload(user), settings.SECRET_KEY, algorithm=jwt_settings["JWT_ALGORITHM"]
    ).decode("utf-8")


def decode_jwt(jwt_token: str) -> int:
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
            jwt_settings["JWT_VERIFY"],
            options={"verify_exp": jwt_settings["JWT_VERIFY_EXPIRATION"],},
            leeway=jwt_settings["JWT_LEEWAY"],
            audience=jwt_settings["JWT_AUDIENCE"],
            issuer=jwt_settings["JWT_ISSUER"],
            algorithms=[jwt_settings["JWT_ALGORITHM"]],
        )
        return payload
    except ExpiredSignatureError:
        raise JSONWebTokenError("Signature expired. Please log in again.")
    except InvalidTokenError:
        raise JSONWebTokenError("Invalid token. Please log in again.")


def refresh_has_expired(orig_iat, context=None) -> bool:
    exp = orig_iat + jwt_settings["JWT_REFRESH_EXPIRATION_DELTA"].total_seconds()
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
    if prefix != jwt_settings["JWT_PREFIX"]:
        raise JSONWebTokenError(
            f"Wrong token prefix in authorization header"
            f"(expecting {jwt_settings['JWT_PREFIX']} got {prefix})"
        )
    # Get the user's id from the JWT
    payload = decode_jwt(jwt_token.split()[1])
    return await user_model.get_by_username(payload.get(user_model.USERNAME_FIELD))


async def get_user_by_payload(payload):
    username = payload.get(user_model.USERNAME_FIELD)

    if not username:
        raise JSONWebTokenError('Invalid payload')

    user = await user_model.get_by_username(username)

    if user is not None and not getattr(user, 'is_active', True):
        raise JSONWebTokenError('User is disabled')
    return user
