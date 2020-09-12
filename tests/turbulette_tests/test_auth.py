import asyncio
from datetime import timedelta
import pytest
from .constants import CUSTOMER_USERNAME, DEFAULT_PASSWORD
from .queries import (
    query_books,
    query_exclusive_books,
    query_get_jwt,
    mutation_create_user,
    query_refresh_jwt,
    mutation_update_password,
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
    from turbulette.core.errors import ErrorCode

    access_token, refresh_token = get_user_tokens

    response = await tester.assert_query_success(
        query=query_refresh_jwt, jwt=refresh_token, op_name="refreshJWT"
    )

    assert response[1]["data"]["refreshJWT"]["accessToken"]

    resp = await tester.assert_query_failed(
        query=query_refresh_jwt, jwt=access_token, op_name="refreshJWT"
    )
    assert (
        resp[1]["errors"][0]["extensions"]["code"]
        == ErrorCode.JWT_INVALID_TOKEN_TYPE.name
    )
    assert "accessToken" not in response[1]["data"]


async def test_login_required(tester, create_user, get_user_tokens):
    await tester.assert_query_success(
        query=query_books, jwt=get_user_tokens[0], op_name="books"
    )

    await tester.assert_query_failed(
        query=query_books, jwt=get_user_tokens[0] + "wrong", op_name="books"
    )


async def test_wrong_signature(tester, get_user_tokens):
    from turbulette.core.errors import ErrorCode

    resp = await tester.assert_query_failed(
        query=query_books, jwt=get_user_tokens[0] + "wrong", op_name="books"
    )
    assert (
        resp[1]["errors"][0]["extensions"]["code"]
        == ErrorCode.JWT_INVALID_SINATURE.name
    )


async def test_jwt_not_properly_formatted(tester, get_user_tokens):
    from turbulette.core.errors import ErrorCode

    # Invalid JWT
    resp = await tester.assert_query_failed(
        query=query_books, jwt="invalid", op_name="books"
    )
    assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_EXPIRED.name

    # Empty JWT
    resp = await tester.assert_query_failed(query=query_books, jwt=" ", op_name="books")
    assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_NOT_FOUND.name

    # Prefix absent
    resp = await tester.assert_query_failed(
        query=query_books,
        headers={"authorization": f"{get_user_tokens[0]}"},
        op_name="books",
    )
    assert (
        resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_INVALID_PREFIX.name
    )

    # Empty authorization header
    resp = await tester.assert_query_failed(
        query=query_books, headers={"authorization": ""}, op_name="books"
    )
    assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_NOT_FOUND.name

    # Invalid JWT header
    header, others = get_user_tokens[0].split(".", maxsplit=1)
    wrong_jwt = header + "__." + others
    resp = await tester.assert_query_failed(
        query=query_books, jwt=wrong_jwt, op_name="books"
    )
    assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_INVALID.name

    # Invalid JWT payload
    header, payload, signature = get_user_tokens[0].split(".")
    wrong_jwt = header + payload + "__." + signature
    resp = await tester.assert_query_failed(
        query=query_books, jwt=wrong_jwt, op_name="books"
    )
    assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_EXPIRED.name


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
    from turbulette.apps.auth.core import get_user_by_claims, decode_jwt
    from turbulette.apps.auth.exceptions import JWTNoUsername, UserDoesNotExists
    from turbulette.apps.auth.core import jwt_payload_from_id, encode_jwt, TokenType

    claims = decode_jwt(get_user_tokens[1])[1]
    user = await get_user_by_claims(claims)

    assert user.username == CUSTOMER_USERNAME

    # Invalid payload
    claims["sub"] = None
    with pytest.raises(JWTNoUsername):
        user = await get_user_by_claims(claims)

    # Invalid user
    false_access_jwt = encode_jwt(jwt_payload_from_id("unknown_id"), TokenType.ACCESS)

    claims = decode_jwt(false_access_jwt)[1]
    with pytest.raises(UserDoesNotExists):
        user = await get_user_by_claims(claims)


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


async def test_access_token_required(tester, get_user_tokens):
    await tester.assert_query_success(
        query=query_exclusive_books, jwt=get_user_tokens[0], op_name="exclusiveBooks"
    )


async def test_token_expired(tester, get_user_tokens):
    from turbulette.conf.utils import settings_stub
    from turbulette.core.errors import ErrorCode

    with settings_stub(JWT_EXPIRATION_DELTA=timedelta(microseconds=1)):
        response = await tester.assert_query_success(
            query=query_get_jwt,
            jwt=get_user_tokens[0],
            op_name="getJWT",
            variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
        )
        await asyncio.sleep(0.05)
        resp = await tester.assert_query_failed(
            query=query_books,
            jwt=response[1]["data"]["getJWT"]["accessToken"],
            op_name="books",
        )
        assert resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_EXPIRED.name


async def test_fresh_token(tester, get_user_tokens):
    from turbulette.conf.utils import settings_stub
    from turbulette.core.errors import ErrorCode

    with settings_stub(JWT_FRESH_DELTA=timedelta(microseconds=1)):
        response = await tester.assert_query_success(
            query=query_get_jwt,
            jwt=get_user_tokens[0],
            op_name="getJWT",
            variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
        )
        await asyncio.sleep(0.05)
        resp = await tester.assert_query_failed(
            query=mutation_update_password,
            jwt=response[1]["data"]["getJWT"]["accessToken"],
            op_name="updatePassword",
            variables={"password": DEFAULT_PASSWORD},
        )
        assert (
            resp[1]["errors"][0]["extensions"]["code"] == ErrorCode.JWT_NOT_FRESH.name
        )

    with settings_stub(JWT_FRESH_DELTA=timedelta(minutes=5)):
        response = await tester.assert_query_success(
            query=query_get_jwt,
            jwt=get_user_tokens[0],
            op_name="getJWT",
            variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
        )
        await asyncio.sleep(0.05)
        resp = await tester.assert_query_success(
            query=mutation_update_password,
            jwt=response[1]["data"]["getJWT"]["accessToken"],
            op_name="updatePassword",
            variables={"password": DEFAULT_PASSWORD},
        )
