from turbulette import query
from turbulette.core.errors import BaseError
from ... import user_model
from ...pyd_models import Token
from ...core import verify_password, encode_jwt, get_payload, get_user_by_payload
from ...exceptions import JSONWebTokenError
from ...decorators import login_required


@query.field("getJWT")
async def resolve_user_token(parent, info, username, password):
    user = await user_model.query.where(user_model.username == username).gino.first()
    error = BaseError()
    if user:
        if verify_password(password, user.hashed_password):
            token = encode_jwt(user)
            return Token(token=token)
        error.add("Invalid password")
        return error.dict()
    error.add(f"User {username} does not exists")
    return error.dict()


@query.field("refreshJWT")
@login_required
async def resolve_refresh_jwt_token(parent, info, token: str):
    payload = get_payload(token)
    user = await get_user_by_payload(payload)
    orig_iat = payload.get('origIat')

    # if not orig_iat:
    #     raise JSONWebTokenError(_('origIat field is required'))

    # if jwt_settings.JWT_REFRESH_EXPIRED_HANDLER(orig_iat, context):
    #     raise JSONWebTokenError(_('Refresh has expired'))

    # payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, context)
    # payload['origIat'] = orig_iat
    # refresh_expires_in = orig_iat +\
    #     jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()

    # token = jwt_settings.JWT_ENCODE_HANDLER(payload, context)
