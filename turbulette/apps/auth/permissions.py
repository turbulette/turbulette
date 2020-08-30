from . import user_model
from .models import Group, GroupPermission, Permission


async def has_scope(username, permissions: list, is_staff=False) -> bool:
    """Check for a user permissions.

    Args:
        user (user_model): The auth user mode specified in settings
        permissions (list): Permissions list to check

    Returns:
        bool: ``True`` if the user has all of the required permissions, ``False`` otherwise
    """
    authorized = True
    user = await user_model.get_by_username(username)
    if permissions:
        query = GroupPermission.load(permission=Permission, group=Group).query.where(
            Group.id == user.permission_group
        )
        group_permissions = await query.gino.all()
        if len(group_permissions) > 0:
            authorized = all(
                any(p == gp.permission.key for gp in group_permissions)
                for p in permissions
            )
        else:
            authorized = False
    if is_staff:
        authorized = user.is_staff
    return authorized
