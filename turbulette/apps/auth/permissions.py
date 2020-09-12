from typing import List
from . import user_model
from .models import Role, RolePermission, Permission, UserRole, UserPermission


async def has_scope(
    username, roles: List[str], permissions: List[str], is_staff=False
) -> bool:
    """Check for a user permissions.

    Args:
        user (user_model): The auth user mode specified in settings
        permissions (list): Permissions list to check

    Returns:
        bool: ``True`` if the user has all of the required permissions, ``False`` otherwise
    """
    authorized = True
    user = await user_model.get_by_username(username)

    if not roles or permissions:
        role_permission = []

        # Load user roles first, with associated permissions.
        # If only `roles` is set, then we want to check for user roles.
        # If only permissions is set, we check first if all required permissions
        # are already granted by roles (so we need to query user roles regardless of
        # the presence of `roles` and `permissions` params)
        query = UserRole.join(Role).join(RolePermission).join(Permission).select()

        # Retrieve user roles with the associated permissions
        role_permission = (
            await query.gino.load(RolePermission.load(role=Role, permission=Permission))
            .query.where(UserRole.user == user.id)
            .gino.all()
        )

        # Check required roles
        if roles:
            if len(role_permission) > 0:
                authorized = all(
                    any(p == role_perm.role.name for role_perm in role_permission)
                    for p in roles
                )
            else:
                authorized = False

        # Check required permissions
        if permissions:
            # We first check if asked permissions are satisfied with those from user roles
            # If so, we don't need to query any other user permissions
            remaining_perms = []
            for perm in permissions:
                if not any(
                    perm == role_perm.permission.key for role_perm in role_permission
                ):
                    remaining_perms.append(perm)

            if remaining_perms:
                query = UserPermission.load(permission=Permission).query.where(
                    UserPermission.user == user.id
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
