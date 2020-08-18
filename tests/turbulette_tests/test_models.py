import pytest
from .constants import CUSTOMER_USERNAME, DEFAULT_PASSWORD

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
async def create_custom_user(create_permission_group):
    from tests.app_1.models import CustomUser

    await CustomUser.create(
        username=CUSTOMER_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{CUSTOMER_USERNAME}@example.com",
        hashed_password=DEFAULT_PASSWORD,
        permission_group=create_permission_group.id,
    )


async def test_repr(tester, create_user_data, create_custom_user):
    from turbulette.apps.auth.models import Group, GroupPermission, Permission
    from tests.app_1.models import BaseUser, CustomUser

    user = await BaseUser.query.where(
        BaseUser.username == CUSTOMER_USERNAME
    ).gino.first()

    assert repr(user) == f"<BaseUser: {user.id}>"

    custom_user = await CustomUser.query.where(
        BaseUser.username == CUSTOMER_USERNAME
    ).gino.first()

    assert repr(custom_user) == f"<CustomUser: {custom_user.username}>"

    group_perm = (
        await GroupPermission.load(permission=Permission, group=Group)
        .query.where(Group.id == user.permission_group)
        .gino.first()
    )
    assert (
        repr(group_perm)
        == f"<GroupPermission: group: {group_perm.group}, permission: {group_perm.permission}>"
    )
    assert repr(group_perm.group) == f"<Group: {group_perm.group.name}>"
    assert repr(group_perm.permission) == f"<Permission: {group_perm.permission.key}>"
