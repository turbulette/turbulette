from enum import Enum
from importlib import import_module
from typing import Tuple
from turbulette.db import db
from gino.declarative import Model
from jwcrypto.jwk import JWK
from jwcrypto.jws import InvalidJWSSignature, InvalidJWSObject
from passlib.context import CryptContext
from python_jwt import generate_jwt, process_jwt, verify_jwt
from turbulette.core.cache import cache
from turbulette.conf import settings
from .models import Permission, Role, RolePermission, UserRole
from gino.loader import TupleLoader

from .exceptions import (
    JWTInvalidSignature,
    JWTDecodeError,
    JWTExpired,
    JWTNoUsername,
    JWTInvalidPrefix,
    JWTNotFound,
)


# Create crypto context
pwd_context = CryptContext(schemes=[settings.HASH_ALGORITHM], deprecated="auto")

# Dynamically import user model
user_model: Model = getattr(
    import_module(settings.AUTH_USER_MODEL.rsplit(".", 1)[0]),
    settings.AUTH_USER_MODEL.rsplit(".", 1)[-1],
)

# Cast secrets to str
_secret_key = JWK(**{key: str(value) for key, value in settings.SECRET_KEY.items()})


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def _jwt_payload(user_id: str, scopes: list, is_staff: bool) -> dict:
    if is_staff:
        scopes.append("_staff")
    payload = {"sub": user_id, "scopes": scopes}

    if settings.JWT_AUDIENCE is not None:
        payload["aud"] = settings.JWT_AUDIENCE

    if settings.JWT_ISSUER is not None:
        payload["iss"] = settings.JWT_ISSUER

    return payload


async def jwt_payload(user: user_model) -> dict:
    return _jwt_payload(user.get_username(), await _get_scopes(user), user.is_staff)


def jwt_payload_from_claims(claims: dict) -> dict:
    return _jwt_payload(claims["sub"], claims["scopes"], "_staff" in claims["scopes"])


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


async def _get_scopes(user: user_model) -> list:
    """Return a list of user role names."""
    query = (
        user_model.join(UserRole)
        .join(Role)
        .join(RolePermission)
        .join(Permission)
        .select()
    )
    role_perms = (
        await query.where(user_model.username == user.username)
        .gino.load(Role.distinct(Role.id).load(add_permission=Permission.load()))
        .query.gino.all()
    )

    for role in role_perms:
        cached_role = await cache.get(role.name)
        if not cached_role:
            permissions = [p.to_dict() for p in role.permissions]
            await cache.set(role.name, permissions)

    return list(map(lambda role: role.name, role_perms))


def process_jwt_header(header: str) -> str:
    if not header:
        raise JWTNotFound()

    prefix, *others = header.split()

    jwt = others[0] if others else None

    if prefix != settings.JWT_PREFIX:
        raise JWTInvalidPrefix(
            f"JWT prefix in the authorization header is invalid,"
            f" got '{prefix}' expected '{settings.JWT_PREFIX}'"
        )

    if not jwt:
        raise JWTNotFound()

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
    except (InvalidJWSObject, UnicodeDecodeError) as error:
        raise JWTDecodeError from error
    except InvalidJWSSignature as error:
        raise JWTInvalidSignature from error
    except Exception as error:
        raise JWTExpired from error


async def get_token_from_user(user: user_model) -> str:
    """A shortcut to get the token directly from a user model instance.

    Args:
        user (user_model): GINO model instance of AUTH_USER_MODEL

    Returns:
        str: The JWT token
    """
    return encode_jwt(await jwt_payload(user), TokenType.ACCESS)


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


async def get_user_by_claims(claims):
    username = claims.get("sub")

    if not username:
        raise JWTNoUsername()

    user = await user_model.get_by_username(username)
    return user
