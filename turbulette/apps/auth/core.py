from enum import Enum
from importlib import import_module
from typing import Tuple

from gino.declarative import Model
from jwcrypto.jwk import JWK
from jwcrypto.jws import InvalidJWSSignature, InvalidJWSObject
from passlib.context import CryptContext
from python_jwt import generate_jwt, process_jwt, verify_jwt

from turbulette.conf import settings

from .exceptions import JWTInvalidSignatureError, JWTDecodeError, JWTExpiredError

# Create crypto context
pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

# Dynamically import user model
user_model: Model = getattr(
    import_module(settings.AUTH_USER_MODEL.rsplit(".", 1)[0]),
    settings.AUTH_USER_MODEL.rsplit(".", 1)[-1],
)

_secret_key = JWK(**settings.SECRET_KEY)


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def _jwt_payload(user_id: str) -> dict:
    payload = {"sub": user_id}

    if settings.JWT_AUDIENCE is not None:
        payload["aud"] = settings.JWT_AUDIENCE

    if settings.JWT_ISSUER is not None:
        payload["iss"] = settings.JWT_ISSUER

    return payload


def jwt_payload(user: user_model) -> dict:
    return _jwt_payload(user.get_username())


def jwt_payload_from_id(user_id: str) -> dict:
    return _jwt_payload(user_id)


def encode_jwt(payload: dict, token_type: TokenType) -> str:

    exp = (
        settings.JWT_EXPIRATION_DELTA
        if token_type is TokenType.ACCESS
        else settings.JWT_REFRESH_EXPIRATION_DELTA
    )

    jti_size = (
        settings.JWT_JTI_SIZE
        if settings.JWT_BLACKLIST_ENABLED
        and token_type.value in settings.JWT_BLACKLIST_TOKEN_CHECKS
        else 0
    )

    payload["type"] = token_type.value
    return generate_jwt(
        payload,
        _secret_key,
        algorithm=settings.JWT_ALGORITHM,
        lifetime=exp,
        jti_size=jti_size,
    )


def process_jwt_header(header: str) -> str:
    if not header:
        raise JWTDecodeError("JWT token not found")

    prefix, *others = header.split()

    jwt = others[0] if others else None

    if prefix != settings.JWT_PREFIX:
        raise JWTDecodeError(
            f"Wrong token prefix in authorization header"
            f"(expecting {settings.JWT_PREFIX} got {prefix})"
        )

    if not jwt:
        raise JWTDecodeError("JWT token not found")

    return jwt


def decode_jwt(jwt: str) -> Tuple:
    """Decode JSON web token.

    Args:
        auth_token (str): The JSON web token

    Raises:
        JSONWebTokenError: Raised if the signature has expired or if the token is invalid

    Returns:
        int: The user id
    """
    if not settings.JWT_VERIFY:
        return process_jwt(jwt)

    try:
        return verify_jwt(
            jwt,
            _secret_key,
            checks_optional=settings.JWT_VERIFY_EXPIRATION,
            iat_skew=settings.JWT_LEEWAY,
            allowed_algs=[settings.JWT_ALGORITHM],
        )
    except (InvalidJWSObject, UnicodeDecodeError):
        raise JWTDecodeError("JWT is invalid and/or improperly formatted")
    except InvalidJWSSignature:
        raise JWTInvalidSignatureError
    except Exception:
        raise JWTExpiredError


def get_token_from_user(user: user_model) -> str:
    """A shortcut to get the token directly from a user model instance.

    Args:
        user (user_model): GINO model instance of AUTH_USER_MODEL

    Returns:
        str: The JWT token
    """
    return encode_jwt(jwt_payload(user), TokenType.ACCESS)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check the password against an existing hash.

    Args:
        plain_password (str): Plain password to check
        hashed_password (str): Hashed password to compare to

    Returns:
        bool: ``True`` if the password matched the hash, else ``False``
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get the password hash.

    Args:
        password (str): The password to hash

    Returns:
        str: The resulting hash
    """
    return pwd_context.hash(password)


async def get_user_by_payload(claims):
    username = claims.get("sub")

    if not username:
        raise JWTDecodeError("Invalid payload")

    user = await user_model.get_by_username(username)
    return user
