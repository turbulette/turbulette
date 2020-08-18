from string import ascii_lowercase
from typing import Any, Dict

import pytest

from turbulette.test.pytest_plugin import (
    create_db,
    db_name,
    event_loop,
    project_settings,
    tester,
    turbulette_setup,
)
from turbulette.utils.crypto import get_random_string

from .constants import CUSTOMER_USERNAME, DEFAULT_PASSWORD, STAFF_USERNAME
from .queries import query_get_jwt


@pytest.fixture(scope="session")
async def create_permission_group(turbulette_setup):
    from turbulette.apps.auth.models import Group, GroupPermission, Permission

    group = await Group.create(name="customer")
    permission = await Permission.create(key="book:borrow", name="Can borrow a book")
    await GroupPermission.create(group=group.id, permission=permission.id)
    return group


@pytest.fixture(scope="session")
async def create_user(create_permission_group):
    from turbulette.apps.auth.utils import create_user

    await create_user(
        username=CUSTOMER_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{CUSTOMER_USERNAME}@example.com",
        password_one=DEFAULT_PASSWORD,
        password_two=DEFAULT_PASSWORD,
        permission_group=create_permission_group.name,
    )


@pytest.fixture(scope="session")
async def create_staff_user(turbulette_setup):
    from turbulette.apps.auth.models import Group, GroupPermission, Permission
    from turbulette.apps.auth.utils import create_user

    group = await Group.create(name="admin")
    permission = await Permission.create(key="books:add", name="Can buy a product")
    await GroupPermission.create(group=group.id, permission=permission.id)
    await create_user(
        username=STAFF_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{STAFF_USERNAME}@example.com",
        password_one=DEFAULT_PASSWORD,
        password_two=DEFAULT_PASSWORD,
        permission_group="admin",
        is_staff=True,
    )


@pytest.fixture
async def get_user_tokens(turbulette_setup, tester):
    response = await tester.assert_query_success(
        query=query_get_jwt,
        variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
        op_name="getJWT",
    )

    assert response[1]["data"]["getJWT"]["accessToken"]
    assert response[1]["data"]["getJWT"]["refreshToken"]

    return (
        response[1]["data"]["getJWT"]["accessToken"],
        response[1]["data"]["getJWT"]["refreshToken"],
    )


@pytest.fixture
async def get_staff_tokens(turbulette_setup, tester):
    response = await tester.assert_query_success(
        query=query_get_jwt,
        variables={"username": STAFF_USERNAME, "password": DEFAULT_PASSWORD},
        op_name="getJWT",
    )

    assert response[1]["data"]["getJWT"]["accessToken"]
    assert response[1]["data"]["getJWT"]["refreshToken"]
    assert not response[1]["data"]["getJWT"]["errors"]

    return (
        response[1]["data"]["getJWT"]["accessToken"],
        response[1]["data"]["getJWT"]["refreshToken"],
    )


@pytest.fixture
async def create_user_data() -> Dict[str, Any]:
    username = get_random_string(10, ascii_lowercase)
    return {
        "username": username,
        "firstName": "John",
        "lastName": "Doe",
        "email": f"{username}@example.com",
        "passwordOne": DEFAULT_PASSWORD,
        "passwordTwo": DEFAULT_PASSWORD,
    }
