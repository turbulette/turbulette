import pytest

from turbulette.core.errors import ErrorCode

from .constants import CUSTOMER_PERMISSION, CUSTOMER_USERNAME
from .queries import (
    mutation_add_book,
    mutation_borrow_book,
    mutation_destroy_library,
    query_borrowings,
    query_borrowings_price_bought,
    query_comics,
)

pytestmark = pytest.mark.asyncio


async def test_role_permission(
    tester,
    create_user,
    create_book,
    create_staff_user,
    create_user_no_role,
    get_no_role_user_tokens,
    get_staff_tokens,
    get_user_tokens,
):
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
        errors=False,
        variables={"id": create_book.id},
        error_codes=[ErrorCode.QUERY_NOT_ALLOWED],
    )

    response = await tester.assert_query_failed(
        query=mutation_borrow_book,
        op_name="borrowBook",
        jwt=get_no_role_user_tokens[0],
        variables={"id": create_book.id},
        errors=False,
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
        errors=False,
        error_codes=[ErrorCode.QUERY_NOT_ALLOWED],
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
    tester,
    create_user,
    get_user_tokens,
    create_staff_user,
    get_staff_tokens,
    create_book,
):
    await tester.assert_query_success(
        query=query_borrowings,
        jwt=get_staff_tokens[0],
        op_name="book",
        variables={"id": create_book.id},
    )

    await tester.assert_query_success(
        query=query_comics, jwt=get_user_tokens[0], op_name="comics"
    )


async def test_deny_field_permission(tester, create_user, get_user_tokens, create_book):
    resp = await tester.assert_query_success(
        query=query_borrowings,
        jwt=get_user_tokens[0],
        op_name="book",
        variables={"id": create_book.id},
        error_codes=[ErrorCode.FIELD_NOT_ALLOWED],
    )
    # Only one field is denied
    assert len(resp[1]["extensions"]["scope"][ErrorCode.FIELD_NOT_ALLOWED.name]) == 1

    resp = await tester.assert_query_success(
        query=query_borrowings_price_bought,
        jwt=get_user_tokens[0],
        op_name="books",
        error_codes=[ErrorCode.FIELD_NOT_ALLOWED],
    )
    # Two fields are denied
    assert len(resp[1]["extensions"]["scope"][ErrorCode.FIELD_NOT_ALLOWED.name]) == 2


async def test_allow_specific_user(tester, create_staff_user, get_staff_tokens):
    await tester.assert_query_success(
        query=mutation_destroy_library,
        jwt=get_staff_tokens[0],
        op_name="destroyLibrary",
    )


async def test_no_policies_involved(
    tester,
    create_book,
    create_user_no_role,
    get_no_role_user_tokens,
):
    await tester.assert_query_success(
        query=query_borrowings,
        jwt=get_no_role_user_tokens[0],
        op_name="book",
        variables={"id": create_book.id},
        error_codes=[ErrorCode.FIELD_NOT_ALLOWED],
    )
