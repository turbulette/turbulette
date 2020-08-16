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


async def test_create_user(turbulette_setup, tester):
    from turbulette.apps.auth.models import Group, GroupPermission, Permission
    from turbulette.apps.auth.utils import create_user
    from turbulette.apps.auth import core
    from turbulette.apps import auth

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

    access_token = response[1]["data"]["getJWT"]["accessToken"]
    refresh_token = response[1]["data"]["getJWT"]["refreshToken"]

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

    await tester.assert_query_failed(
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


async def test_wrong_signature(turbulette_setup, tester, false_refresh_jwt):
    response = await tester.assert_query_success(
        query="""
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {false_refresh_jwt}___wrong___"},
    )

    assert "errors" in response[1]["data"]["refreshJWT"]


async def test_not_a_refresh_token(turbulette_setup, tester, false_access_jwt):
    # TODO Make `pytest.raises()` working here
    response = await tester.assert_query_failed(
        query="""
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {false_access_jwt}"},
    )
    # We ensure that there is a GraphQL error and that the
    # access token hasn't be produced
    assert not response[1]["data"]["refreshJWT"]


async def test_no_verify(turbulette_setup, tester, false_refresh_jwt):
    turbulette_setup.settings.configure(JWT_VERIFY=False)
    response = await tester.assert_query_success(
        query="""
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
        """,
        headers={"authorization": f"JWT {false_refresh_jwt}"},
    )
    assert not response[1]["data"]["refreshJWT"]["errors"]
