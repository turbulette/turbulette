import pytest
from .constants import CUSTOMER_USERNAME, DEFAULT_PASSWORD
from .queries import mutation_create_comic

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
async def create_custom_user(create_permission_role):
    from tests.app_1.models import CustomUser

    await CustomUser.create(
        username=CUSTOMER_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{CUSTOMER_USERNAME}@example.com",
        hashed_password=DEFAULT_PASSWORD,
        permission_role=create_permission_role.id,
    )


async def test_repr(tester, create_user_data, create_custom_user):
    from turbulette.apps.auth.models import Role, RolePermission, Permission
    from tests.app_1.models import BaseUser, CustomUser

    user = await BaseUser.query.where(
        BaseUser.username == CUSTOMER_USERNAME
    ).gino.first()

    assert repr(user) == f"<BaseUser: {user.id}>"

    custom_user = await CustomUser.query.where(
        BaseUser.username == CUSTOMER_USERNAME
    ).gino.first()

    assert repr(custom_user) == f"<CustomUser: {custom_user.username}>"

    role_perm = (
        await RolePermission.load(permission=Permission, role=Role)
        .query.where(Role.id == user.permission_role)
        .gino.first()
    )
    assert (
        repr(role_perm)
        == f"<RolePermission: role: {role_perm.role}, permission: {role_perm.permission}>"
    )
    assert repr(role_perm.role) == f"<Role: {role_perm.role.name}>"
    assert repr(role_perm.permission) == f"<Permission: {role_perm.permission.key}>"


async def test_validate_models(tester):
    """Test validate decorator with multiple models."""
    await tester.assert_query_success(
        query=mutation_create_comic,
        op_name="createComic",
        variables={
            "title": "The Adventures of Tintin",
            "author": "Hergé",
            "publicationDate": "1929-07-20T12:00:12",
            "profile": '{"genre": ["action", "adventure"]}',
            "artist": "Hergé",
        },
    )
