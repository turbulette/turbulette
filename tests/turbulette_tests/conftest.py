from datetime import datetime
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
    blank_conf,
)
from turbulette.utils.crypto import get_random_string

from .constants import (
    CUSTOMER_USERNAME,
    DEFAULT_PASSWORD,
    STAFF_USERNAME,
    CUSTOMER_PERMISSION,
    NO_ROLE_USERNAME,
)
from .queries import query_get_jwt


@pytest.fixture(scope="session")
async def create_permission_role(turbulette_setup):
    from turbulette.apps.auth.models import Role, RolePermission, Permission

    role = await Role.create(name="customer")
    permission = await Permission.create(
        key=CUSTOMER_PERMISSION, name="Can borrow a book"
    )
    await RolePermission.create(role=role.id, permission=permission.id)
    return role


@pytest.fixture(scope="session")
async def create_user(create_permission_role):
    from turbulette.apps.auth.utils import create_user

    await create_user(
        username=CUSTOMER_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{CUSTOMER_USERNAME}@example.com",
        password_one=DEFAULT_PASSWORD,
        password_two=DEFAULT_PASSWORD,
        role=create_permission_role.name,
    )


@pytest.fixture(scope="session")
async def create_staff_user(turbulette_setup):
    from turbulette.apps.auth.models import Role, RolePermission, Permission
    from turbulette.apps.auth.utils import create_user

    role = await Role.create(name="admin")
    permission = await Permission.create(key="books:add", name="Can buy a product")
    await RolePermission.create(role=role.id, permission=permission.id)
    return await create_user(
        username=STAFF_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{STAFF_USERNAME}@example.com",
        password_one=DEFAULT_PASSWORD,
        password_two=DEFAULT_PASSWORD,
        role="admin",
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


@pytest.fixture(scope="session")
async def create_book():
    from tests.app_1.models import Book

    book = await Book.create(
        title="The Lord of the Rings",
        author="J.R.R Tolkien",
        publication_date=datetime(year=1999, month=7, day=20, hour=12, second=12),
        profile={"genre": ["fantasy"], "awards": []},
    )
    return book


@pytest.fixture(scope="session")
async def create_user_no_role():
    from turbulette.apps.auth.utils import create_user

    user_no_role = await create_user(
        username=NO_ROLE_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{NO_ROLE_USERNAME}@email.com",
        password_one="1234",
        password_two="1234",
    )


@pytest.fixture
async def get_no_role_user_tokens(tester):
    response = await tester.assert_query_success(
        query=query_get_jwt,
        variables={"username": NO_ROLE_USERNAME, "password": DEFAULT_PASSWORD},
        op_name="getJWT",
    )

    assert response[1]["data"]["getJWT"]["accessToken"]
    assert response[1]["data"]["getJWT"]["refreshToken"]

    return (
        response[1]["data"]["getJWT"]["accessToken"],
        response[1]["data"]["getJWT"]["refreshToken"],
    )
