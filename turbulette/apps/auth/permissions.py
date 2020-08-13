from . import user_model
from .models import Group, GroupPermission, Permission


async def has_permission(user: user_model, permissions: list) -> bool:
    """Check for a user permissions

    Args:
        user (user_model): The auth user mode specified in settings
        permissions (list): Permissions list to check

    Returns:
        bool: ``True`` if the user has all of the required permissions, ``False`` otherwise
    """
    query = GroupPermission.load(permission=Permission).query.where(
        Group.id == user.permission_group
    )
    group_permissions = await query.gino.all()
    if len(group_permissions) == 0:
        return False
    return all(
        any(p == gp.permission.key for gp in group_permissions) for p in permissions
    )
