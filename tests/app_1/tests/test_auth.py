import pytest

# Needed to make fixtures available
from turbulette.test.pytest_plugin import (
    gino_engine,
    create_db,
    db_name,
    project_settings,
    event_loop,
    tester,
)


@pytest.mark.asyncio
async def test_create_user(gino_engine, tester):
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

    response = await tester.assert_query_success(
        query="""
            query {
                getJWT(username: "test_user", password: "1234"){
                    token
                    errors
                }
            }
        """
    )

    assert response[1]["data"]["getJWT"]["token"]
    token = response[1]["data"]["getJWT"]["token"]

    await tester.assert_query_success(
        query="""
            query refreshJWT($token: String!) {
                refreshJWT(token: $token){
                    token
                    errors
                }
            }
        """,
        variables={"token": token},
        headers={"authorization": f"JWT {token}"},
    )
