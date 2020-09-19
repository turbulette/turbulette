import pytest
from .queries import (
    mutation_borrow_book,
    mutation_add_book,
    query_borrowings,
    mutation_destroy_library,
)
from .constants import CUSTOMER_USERNAME, CUSTOMER_PERMISSION
from turbulette.core.errors import ErrorCode

pytestmark = pytest.mark.asyncio


async def test_role_permission(
    tester,
    create_user,
    create_book,
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
        query=mutation_borrow_book,
        jwt=get_user_tokens[0],
        op_name="borrowBook",
        variables={"id": create_book.id},
    )
    assert response[1]["data"]["borrowBook"]["success"]

    # The staff user has not `book:borrow` permission
    response = await tester.assert_query_failed(
        query=mutation_borrow_book,
        jwt=get_staff_tokens[0],
        op_name="borrowBook",
        variables={"id": create_book.id},
        error_codes=[ErrorCode.QUERY_NOT_ALLOWED],
    )

    response = await tester.assert_query_failed(
        query=mutation_borrow_book,
        op_name="borrowBook",
        headers={"authorization": f"JWT {await get_token_from_user(user_no_role)}"},
        variables={"id": create_book.id},
        error_codes=[ErrorCode.QUERY_NOT_ALLOWED],
    )


async def test_staff_member(
    tester, create_staff_user, get_staff_tokens, get_user_tokens
):
    response = await tester.assert_query_success(
        query=mutation_add_book, jwt=get_staff_tokens[0], op_name="addBook"
    )

    assert response[1]["data"]["addBook"]["success"]

    response = await tester.assert_query_failed(
        query=mutation_add_book,
        jwt=get_user_tokens[0],
        op_name="addBook",
    )


async def test_get_role_permissions(tester, create_user):
    from tests.app_1.models import BaseUser

    user = await BaseUser.get_by_username(CUSTOMER_USERNAME)
    role_perms = await user.get_perms()
    assert len(role_perms) == 1
    assert role_perms[0].key == CUSTOMER_PERMISSION


async def test_role_crud(tester):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth.models import Role
    from turbulette.db.exceptions import DoesNotExist

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

    # Error handling
    with pytest.raises(DoesNotExist):
        await user.remove_role(name="unknow")

    with pytest.raises(Exception):
        await user.add_role()


async def test_field_permission(
    tester, create_staff_user, get_staff_tokens, create_book
):
    await tester.assert_query_success(
        query=query_borrowings,
        jwt=get_staff_tokens[0],
        op_name="book",
        variables={"id": create_book.id},
    )


async def test_deny_field_permission(tester, create_user, get_user_tokens, create_book):
    await tester.assert_query_success(
        query=query_borrowings,
        jwt=get_user_tokens[0],
        op_name="book",
        variables={"id": create_book.id},
        error_codes=[ErrorCode.FIELD_NOT_ALLOWED],
    )


async def test_allow_specific_user(
    tester, create_staff_user, get_staff_tokens, create_book
):
    await tester.assert_query_success(
        query=mutation_destroy_library,
        jwt=get_staff_tokens[0],
        op_name="destroyLibrary",
    )
