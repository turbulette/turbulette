from typing import Tuple
from turbulette import query
from turbulette.conf import settings
from turbulette.core.errors import BaseError

from ... import user_model
from ...core import (
    TokenType,
    encode_jwt,
    jwt_payload,
    jwt_payload_from_id,
    verify_password,
)
from ...decorators import refresh_token_required
from ...pyd_models import AccessToken, Token


@query.field("getJWT")
async def get_jwt(_, __, username, password):
    user = await user_model.query.where(user_model.username == username).gino.first()
    error = BaseError()
    if user:
        if verify_password(password, user.hashed_password):
            payload = jwt_payload(user)
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
async def refresh_jwt_token(_, __, jwt_claims: Tuple):
    id_ = jwt_claims.get(user_model.USERNAME_FIELD)
    payload = jwt_payload_from_id(id_)
    return AccessToken(access_token=encode_jwt(payload, TokenType.ACCESS))
