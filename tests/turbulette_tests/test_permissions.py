import pytest
from .queries import mutation_borrow_books, mutation_add_book, mutation_borrow_unlimited
from .constants import CUSTOMER_USERNAME, CUSTOMER_PERMISSION

pytestmark = pytest.mark.asyncio


async def test_role_permission(
    tester,
    create_user,
    create_staff_user,
    get_staff_tokens,
    get_user_tokens,
):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth import get_token_from_user

    user_no_role = await create_user(
        username="test_user_no_role",
        first_name="test",
        last_name="user",
        email="no_role@email.com",
        password_one="1234",
        password_two="1234",
    )

    response = await tester.assert_query_success(
        query=mutation_borrow_books, jwt=get_user_tokens[0], op_name="borrowBook"
    )
    assert response[1]["data"]["borrowBook"]["success"]

    # The staff user has not `book:borrow` permission
    response = await tester.assert_query_success(
        query=mutation_borrow_books,
        jwt=get_staff_tokens[0],
        op_name="borrowBook",
        op_errors=True,
    )
    assert not response[1]["data"]["borrowBook"]["success"]

    response = await tester.assert_query_success(
        query=mutation_borrow_books,
        op_name="borrowBook",
        op_errors=True,
        headers={"authorization": f"JWT {get_token_from_user(user_no_role)}"},
    )
    assert not response[1]["data"]["borrowBook"]["success"]


async def test_staff_member(
    tester, create_staff_user, get_staff_tokens, get_user_tokens
):
    response = await tester.assert_query_success(
        query=mutation_add_book, jwt=get_staff_tokens[0], op_name="addBook"
    )

    assert response[1]["data"]["addBook"]["success"]

    response = await tester.assert_query_success(
        query=mutation_add_book,
        jwt=get_user_tokens[0],
        op_name="addBook",
        op_errors=True,
    )


async def test_custom_permissions(tester):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth import get_token_from_user
    from turbulette.apps.auth.models import Permission, UserPermission

    perm_key = "book:borrow-unlimited"
    user = await create_user(
        username="test_user_custom_permission",
        first_name="test",
        last_name="user",
        email="custom_perm@email.com",
        password_one="1234",
        password_two="1234",
    )

    permission = await Permission.create(name="Borrow unlimited books", key=perm_key)
    await UserPermission.create(user=user.id, permission=permission.id)

    await tester.assert_query_success(
        query=mutation_borrow_unlimited,
        op_name="borrowUnlimitedBooks",
        jwt=get_token_from_user(user),
    )
    perm = await user.get_perms()
    assert len(perm) == 1
    assert perm[0].key == perm_key


async def test_get_role_permissions(tester, create_user):
    from tests.app_1.models import BaseUser

    user = await BaseUser.get_by_username(CUSTOMER_USERNAME)
    role_perms = await user.get_role_perms()
    assert len(role_perms) == 1
    assert role_perms[0].key == CUSTOMER_PERMISSION


async def test_perm_crud(tester):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth.models import Permission
    from turbulette.db.exceptions import DoesNotExist

    user = await create_user(
        username="test_user_add_permission",
        first_name="test",
        last_name="user",
        email="add_perm@email.com",
        password_one="1234",
        password_two="1234",
    )

    perm_key = "new:permission"
    perm = await Permission.create(name="New permission", key=perm_key)

    # Get perm
    user_perm = await user.get_perms()
    assert not user_perm

    # Add perm using permission object
    await user.add_perm(permission=perm)

    user_perm = await user.get_perms()
    assert user_perm[0].key == perm_key

    # No args
    with pytest.raises(Exception):
        await user.add_perm()

    # Invalid permission key
    with pytest.raises(DoesNotExist):
        await user.add_perm(key="unknown_perm")

    # Remove perm using key
    await user.remove_perm(key=perm_key)
    user_perm = await user.get_perms()
    assert not user_perm


async def test_role_crud(tester):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth.models import Role

    user = await create_user(
        username="test_user_crud_role",
        first_name="test",
        last_name="user",
        email="crud_role@email.com",
        password_one="1234",
        password_two="1234",
    )

    role_name = "employee"
    role = await Role.create(name=role_name)

    user_roles = await user.get_roles()
    assert len(user_roles) == 0

    # Add role
    await user.add_role(name=role_name)
    user_roles = await user.get_roles()
    assert len(user_roles) == 1
    assert user_roles[0].name == role_name

    # Remove role
    await user.remove_role(role=role)
    user_roles = await user.get_roles()
    assert len(user_roles) == 0
