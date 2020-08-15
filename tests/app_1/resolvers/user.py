from ariadne import convert_kwargs_to_snake_case
from turbulette import mutation
from turbulette.apps.auth import user_model, get_token_from_user
from turbulette.apps.auth.pyd_models import BaseUserCreate
from turbulette.apps.auth.utils import create_user
from turbulette.core.errors import BaseError
from turbulette.core.validation.decorators import validate


@mutation.field("createUser")
@convert_kwargs_to_snake_case
@validate(models=[BaseUserCreate])
async def resolve_user_create(obj, info, valid_input, **kwargs) -> dict:
    user_data = valid_input[0]
    user = await user_model.query.where(
        user_model.username == user_data["username"]
    ).gino.first()

    if user:
        return BaseError(f"User {user_data['username']} already exists").dict()

    new_user = await create_user(**user_data, permission_group="customer")
    # new_fan = await BaseUser.create(**fan_data, user=new_user.id)
    auth_token = get_token_from_user(new_user)
    return {
        "user": {**new_user.to_dict()},
        "token": auth_token,
    }
