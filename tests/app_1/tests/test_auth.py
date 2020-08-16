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


async def test_login_required(turbulette_setup, create_user, get_tokens, tester):
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


async def test_jwt_not_properly_formatted(turbulette_setup, tester, false_access_jwt):
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
        headers={"authorization": f"JWT {false_access_jwt}___wrong___"},
    )

    assert "errors" in response[1]["data"]["books"]
    assert not response[1]["data"]["books"]["books"]


async def test_wrong_signature(turbulette_setup, tester, false_access_jwt):
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

    assert "errors" in response[1]["data"]["books"]
    assert not response[1]["data"]["books"]["books"]

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
        headers={"authorization": f"JWT "},
    )

    assert "errors" in response[1]["data"]["books"]
    assert not response[1]["data"]["books"]["books"]

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
        headers={"authorization": f"{false_access_jwt}"},
    )

    assert "errors" in response[1]["data"]["books"]
    assert not response[1]["data"]["books"]["books"]

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
        headers={"authorization": ""},
    )

    assert "errors" in response[1]["data"]["books"]
    assert not response[1]["data"]["books"]["books"]



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
