from .core import get_password_hash
from . import user_model
from .models import Role


async def create_user(role=None, **user_data):
    """Helper to create a user using the mode defined by the `AUTH_USER_MODEL` setting.

    It will create the user with the hashed password add it in the given `role`
    """
    user_role = await Role.query.where(Role.name == role).gino.first() if role else None
    password = user_data.pop("password_one")
    del user_data["password_two"]
    return await user_model.create(
        **user_data,
        hashed_password=get_password_hash(password),
        role=(user_role.id if user_role else None),
    )
