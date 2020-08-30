from .core import get_password_hash
from . import user_model
from .models import Group


async def create_user(permission_group=None, **user_data):
    """Helper to create a user using the mode defined by the `AUTH_USER_MODEL` setting.

    It will create the user with the hashed password add it in the given `group`
    """
    user_group = await Group.query.where(Group.name == permission_group).gino.first()
    password = user_data.pop("password_one")
    del user_data["password_two"]
    return await user_model.create(
        **user_data,
        hashed_password=get_password_hash(password),
        permission_group=(user_group.id if user_group else None),
    )
