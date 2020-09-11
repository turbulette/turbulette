from . import user_model
from .models import Role, RolePermission, Permission


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
        query = RolePermission.load(permission=Permission, role=Role).query.where(
            Role.id == user.role
        )
        role_permissions = await query.gino.all()
        if len(role_permissions) > 0:
            authorized = all(
                any(p == gp.permission.key for gp in role_permissions)
                for p in permissions
            )
        else:
            authorized = False
    if is_staff:
        authorized = user.is_staff
    return authorized
