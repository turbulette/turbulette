import pytest
from .queries import mutation_borrow_books, mutation_add_book, mutation_borrow_unlimited

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

    user = await create_user(
        username="test_user_custom_permission",
        first_name="test",
        last_name="user",
        email="custom_perm@email.com",
        password_one="1234",
        password_two="1234",
    )

    permission = await Permission.create(
        name="Borrow unlimited books", key="book:borrow-unlimited"
    )
    await UserPermission.create(user=user.id, permission=permission.id)

    await tester.assert_query_success(
        query=mutation_borrow_unlimited,
        op_name="borrowUnlimitedBooks",
        jwt=get_token_from_user(user),
    )
