import asyncio
from datetime import timedelta
import pytest
from .constants import CUSTOMER_USERNAME, DEFAULT_PASSWORD
from .queries import (
    mutation_add_book,
    query_books,
    query_exclusive_books,
    query_get_jwt,
    mutation_create_user,
    mutation_borrow_books,
    query_refresh_jwt,
)


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "username,password,errors",
    [
        (CUSTOMER_USERNAME, DEFAULT_PASSWORD, False),
        (CUSTOMER_USERNAME, "invalid", True),
        ("invalid", DEFAULT_PASSWORD, True),
    ],
)
async def test_get_tokens(tester, create_user, username, password, errors):
    # Valid password
    response = await tester.assert_query_success(
        query_get_jwt,
        op_name="getJWT",
        op_errors=errors,
        variables={"username": username, "password": password},
    )

    res = (
        response[1]["data"]["getJWT"]["refreshToken"]
        and response[1]["data"]["getJWT"]["accessToken"]
    )
    if errors:
        assert not res
    else:
        assert res


async def test_refresh_jwt(tester, create_user, get_user_tokens):
    access_token, refresh_token = get_user_tokens

    response = await tester.assert_query_success(
        query=query_refresh_jwt, jwt=refresh_token, op_name="refreshJWT"
    )

    assert response[1]["data"]["refreshJWT"]["accessToken"]

    response = await tester.assert_query_failed(
        query=query_refresh_jwt, jwt=access_token, op_name="refreshJWT"
    )

    assert "accessToken" not in response[1]["data"]

    response = await tester.assert_query_failed(
        query=query_refresh_jwt, jwt=f"{refresh_token}__wrong__", op_name="refreshJWT"
    )


async def test_login_required(tester, create_user, get_user_tokens):
    await tester.assert_query_success(
        query=query_books, jwt=get_user_tokens[0], op_name="books"
    )

    await tester.assert_query_failed(
        query=query_books, jwt=get_user_tokens[0] + "wrong", op_name="books"
    )


async def test_wrong_signature(tester, get_user_tokens):
    await tester.assert_query_failed(
        query=query_books, jwt=get_user_tokens[0] + "wrong", op_name="books"
    )


async def test_jwt_not_properly_formatted(tester, get_user_tokens):
    # Invalid JWT
    response = await tester.assert_query_failed(
        query=query_books, jwt="invalid", op_name="books"
    )

    # Empty JWT
    response = await tester.assert_query_failed(
        query=query_books, jwt=" ", op_name="books"
    )

    # Prefix absent
    response = await tester.assert_query_failed(
        query=query_books,
        headers={"authorization": f"{get_user_tokens[0]}"},
        op_name="books",
    )

    # Empty authorization header
    response = await tester.assert_query_failed(
        query=query_books, headers={"authorization": ""}, op_name="books"
    )

    # Invalid JWT header
    header, others = get_user_tokens[0].split(".", maxsplit=1)
    wrong_jwt = header + "__." + others
    response = await tester.assert_query_failed(
        query=query_books, jwt=wrong_jwt, op_name="books"
    )

    # Invalid JWT payload
    header, payload, signature = get_user_tokens[0].split(".")
    wrong_jwt = header + payload + "__." + signature
    response = await tester.assert_query_failed(
        query=query_books, jwt=wrong_jwt, op_name="books"
    )


async def test_no_verify(tester, get_user_tokens):
    from turbulette.conf.utils import settings_stub

    with settings_stub(JWT_VERIFY=False):
        response = await tester.assert_query_success(
            query=query_refresh_jwt,
            jwt=get_user_tokens[1] + "wrong",
            op_name="refreshJWT",
        )
        assert response[1]["data"]["refreshJWT"]["accessToken"]


async def test_get_token_from_user(tester, create_user):
    from tests.app_1.models import BaseUser
    from turbulette.apps.auth import get_token_from_user

    user = await BaseUser.get_by_username(CUSTOMER_USERNAME)
    access_token = get_token_from_user(user)

    # Check token is valid
    await tester.assert_query_success(
        query=query_books, jwt=access_token, op_name="books"
    )


async def test_get_user_by_payload(tester, create_user, get_user_tokens):
    from turbulette.apps.auth.core import get_user_by_payload, decode_jwt
    from turbulette.apps.auth.exceptions import JWTDecodeError, UserDoesNotExists
    from turbulette.apps.auth.core import jwt_payload_from_id, encode_jwt, TokenType

    claims = decode_jwt(get_user_tokens[1])[1]
    user = await get_user_by_payload(claims)

    assert user.username == CUSTOMER_USERNAME

    # Invalid payload
    claims["sub"] = None
    with pytest.raises(JWTDecodeError):
        user = await get_user_by_payload(claims)

    # Invalid user
    false_access_jwt = encode_jwt(jwt_payload_from_id("unknown_id"), TokenType.ACCESS)

    claims = decode_jwt(false_access_jwt)[1]
    with pytest.raises(UserDoesNotExists):
        user = await get_user_by_payload(claims)


async def test_create_user(tester, create_user, create_user_data):
    response = await tester.assert_query_success(
        query=mutation_create_user,
        op_name="createUser",
        variables={**create_user_data},
    )

    tester.assert_data_in_response(
        response[1]["data"]["createUser"]["user"], create_user_data
    )

    # Test with invalid password
    create_user_data["passwordTwo"] = create_user_data["passwordOne"] + "different"
    response = await tester.assert_query_success(
        query=mutation_create_user,
        op_name="createUser",
        variables={**create_user_data},
        op_errors=True,
    )

    assert not response[1]["data"]["createUser"]["user"]
    create_user_data["passwordTwo"] = create_user_data["passwordOne"]

    # User already exists
    response = await tester.assert_query_success(
        query=mutation_create_user,
        op_name="createUser",
        variables={**create_user_data, "username": CUSTOMER_USERNAME},
        op_errors=True,
    )

    assert not response[1]["data"]["createUser"]["user"]


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


async def test_permission(
    tester, create_staff_user, get_staff_tokens, get_user_tokens,
):
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth import get_token_from_user

    user_no_group = await create_user(
        username="test_user_no_group",
        first_name="test",
        last_name="user",
        email="no_group@email.com",
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
        headers={"authorization": f"JWT {get_token_from_user(user_no_group)}"},
    )
    assert not response[1]["data"]["borrowBook"]["success"]


async def test_access_token_required(tester, get_user_tokens):
    await tester.assert_query_success(
        query=query_exclusive_books, jwt=get_user_tokens[0], op_name="exclusiveBooks"
    )


async def test_token_expired(tester, get_user_tokens):
    from turbulette.conf.utils import settings_stub

    with settings_stub(JWT_EXPIRATION_DELTA=timedelta(microseconds=1)):
        response = await tester.assert_query_success(
            query=query_get_jwt,
            jwt=get_user_tokens[0],
            op_name="getJWT",
            variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
        )
        await asyncio.sleep(0.05)
        await tester.assert_query_failed(
            query=query_books,
            jwt=response[1]["data"]["getJWT"]["accessToken"],
            op_name="getJWT",
        )
