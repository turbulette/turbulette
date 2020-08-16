from base64 import decode
from collections import UserString
from importlib import reload
import pytest

# Needed to make fixtures available
from turbulette.test.pytest_plugin import (
    conf_module,
    turbulette_setup,
    create_db,
    db_name,
    project_settings,
    event_loop,
    tester,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def false_access_jwt():
    from turbulette.apps.auth.core import jwt_payload_from_id, encode_jwt, TokenType

    return encode_jwt(jwt_payload_from_id("unknown_id"), TokenType.ACCESS)


@pytest.fixture
def false_refresh_jwt():
    from turbulette.apps.auth.core import jwt_payload_from_id, encode_jwt, TokenType

    return encode_jwt(jwt_payload_from_id("unknown_id"), TokenType.REFRESH)


@pytest.fixture(scope="module")
async def create_user(turbulette_setup):
    from turbulette.apps.auth.models import Group, GroupPermission, Permission
    from turbulette.apps.auth.utils import create_user

    group = await Group.create(name="customer")
    permission = await Permission.create(key="buy:product", name="Can buy a product")
    await GroupPermission.create(group=group.id, permission=permission.id)
    await create_user(
        username="test_user",
        first_name="test",
        last_name="user",
        email="example@email.com",
        password_one="1234",
        password_two="1234",
        permission_group="customer",
    )


@pytest.fixture
async def get_tokens(turbulette_setup, tester):
    response = await tester.assert_query_success(
        query="""
            query {
                getJWT(username: "test_user", password: "1234"){
                    accessToken
                    refreshToken
                    errors
                }
            }
        """
    )

    assert response[1]["data"]["getJWT"]["accessToken"]
    assert response[1]["data"]["getJWT"]["refreshToken"]

    return (
        response[1]["data"]["getJWT"]["accessToken"],
        response[1]["data"]["getJWT"]["refreshToken"],
    )


async def test_refresh_jwt(turbulette_setup, create_user, get_tokens, tester):
    access_token, refresh_token = get_tokens

    response = await tester.assert_query_success(
        query="""
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {refresh_token}"},
    )

    assert response[1]["data"]["refreshJWT"]["accessToken"]

    response = await tester.assert_query_failed(
        query="""
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {access_token}"},
    )

    assert "accessToken" not in response[1]["data"]


async def test_login_required(turbulette_setup, create_user, get_tokens, false_access_jwt, tester):
    response = await tester.assert_query_success(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {get_tokens[0]}"},
    )

    assert response[1]["data"]["books"]["books"]

    response = await tester.assert_query_success(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {false_access_jwt}"},
    )

    assert not response[1]["data"]["books"]["books"]


async def test_wrong_signature(turbulette_setup, tester, get_tokens):
    from string import ascii_lowercase

    access_token_signature = get_tokens[0].split('.')[-1]
    last_char = ""

    for c in ascii_lowercase:
        if c is not access_token_signature[-1]:
            last_char = c
            break

    wrong_signature = access_token_signature[:-1] + last_char
    access_token = '.'.join(get_tokens[0].split('.')[:2] + [wrong_signature])
    response = await tester.assert_query_failed(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={
            "authorization": f"JWT {access_token}"
        },
    )

    assert not response[1]["data"]["books"]


async def test_jwt_not_properly_formatted(turbulette_setup, tester, false_access_jwt):
    response = await tester.assert_query_failed(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": "JWT invalid"},
    )

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT "},
    )

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": f"{false_access_jwt}"},
    )

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": ""},
    )

    assert not response[1]["data"]["books"]


async def test_no_verify(turbulette_setup, tester, false_refresh_jwt):
    turbulette_setup.settings.configure(JWT_VERIFY=False)
    response = await tester.assert_query_success(
        query="""
            query {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {false_refresh_jwt}"},
    )
    assert not response[1]["data"]["refreshJWT"]["errors"]
    assert response[1]["data"]["refreshJWT"]["accessToken"]


async def test_get_token_from_user(turbulette_setup, create_user, tester):
    from tests.app_1.models import BaseUser
    from turbulette.apps.auth import get_token_from_user

    user = await BaseUser.get_by_username("test_user")
    access_token = get_token_from_user(user)
    # Check token is valid

    response = await tester.assert_query_success(
        query="""
            query {
                books {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {access_token}"},
    )

    assert not response[1]["data"]["books"]["errors"]
    assert response[1]["data"]["books"]["books"]


async def test_get_user_by_payload(
    turbulette_setup, create_user, get_tokens, false_access_jwt, tester
):
    from turbulette.apps.auth.core import get_user_by_payload, decode_jwt
    from turbulette.apps.auth.exceptions import JSONWebTokenError, UserDoesNotExists
    from tests.app_1.models import BaseUser

    claims = decode_jwt(get_tokens[1])[1]
    user = await get_user_by_payload(claims)

    assert user.username == "test_user"

    # Invalid payload
    claims["sub"] = None

    with pytest.raises(JSONWebTokenError):
        user = await get_user_by_payload(claims)

    # Invalid user
    claims = decode_jwt(false_access_jwt)[1]
    with pytest.raises(UserDoesNotExists):
        user = await get_user_by_payload(claims)
