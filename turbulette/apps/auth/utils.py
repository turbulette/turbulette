from .core import get_password_hash
from . import user_model
from .models import Group


async def create_user(permission_group=None, **user_data):
    user_group = await Group.query.where(Group.name == permission_group).gino.first()
    password = user_data.pop("password_one")
    del user_data["password_two"]
    return await user_model.create(
        **user_data,
        hashed_password=get_password_hash(password),
        permission_group=(user_group.id if user_group else None)
    )
