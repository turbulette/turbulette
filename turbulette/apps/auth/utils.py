from .core import get_password_hash
from . import user_model
from .models import Role, UserRole


async def create_user(role=None, **user_data):
    """Helper to create a user using the mode defined by the `AUTH_USER_MODEL` setting.

    It will create the user with the hashed password add it in the given `role`
    """
    password = user_data.pop("password_one")
    del user_data["password_two"]
    user = await user_model.create(
        **user_data,
        hashed_password=get_password_hash(password),
    )
    if role:
        user_role = (
            await Role.query.where(Role.name == role).gino.first() if role else None
        )
        await UserRole.create(user=user.id, role=user_role.id)

    return user
