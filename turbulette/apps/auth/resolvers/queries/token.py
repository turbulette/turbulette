from turbulette import query
from turbulette.conf import settings
from turbulette.errors import ErrorField

from turbulette.apps.auth import user_model
from turbulette.apps.auth.core import (
    TokenType,
    encode_jwt,
    jwt_payload,
    jwt_payload_from_claims,
    verify_password,
)
from turbulette.apps.auth.decorators import refresh_token_required
from turbulette.apps.auth.pyd_models import AccessToken, Token


@query.field("getJWT")
async def get_jwt(_, __, username, password):
    """Get access and refresh token from username and password."""
    user = await user_model.query.where(user_model.username == username).gino.first()
    error = ErrorField()
    if user:
        if verify_password(password, user.hashed_password):
            payload = await jwt_payload(user)
            access_token = encode_jwt(payload, TokenType.ACCESS)
            refresh_token = (
                encode_jwt(payload, TokenType.REFRESH)
                if settings.JWT_REFRESH_ENABLED
                else None
            )
            return Token(access_token=access_token, refresh_token=refresh_token)
        error.add("Invalid password")
        return error.dict()
    error.add(f"User {username} does not exists")
    return error.dict()


@query.field("refreshJWT")
@refresh_token_required
async def refresh_jwt_token(_, __, jwt_claims: dict):
    """Refresh an access token."""
    payload = jwt_payload_from_claims(jwt_claims)
    return AccessToken(access_token=encode_jwt(payload, TokenType.ACCESS))
