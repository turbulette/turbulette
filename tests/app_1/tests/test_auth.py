import pytest
from typing import Dict, Any
from string import ascii_lowercase

# Needed to make fixtures available when testing Turbulette
# without installing it (`poetry install turbulette`)
from turbulette.test.pytest_plugin import (
    turbulette_setup,
    create_db,
    db_name,
    project_settings,
    event_loop,
    tester,
)
from turbulette.utils.crypto import get_random_string

pytestmark = pytest.mark.asyncio

# Fake data
STAFF_USERNAME = "test_user_staff"
CUSTOMER_USERNAME = "test_user"
DEFAULT_PASSWORD = "1234"

# Common queries
get_jwt_query = """
    query getJWT($username: String! $password: String!) {
        getJWT(username: $username, password: $password){
            accessToken
            refreshToken
            errors
        }
    }
"""

books_query = """
        query {
            books {
                books {
                    title
                    author
                }
                errors
            }
        }
"""


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
    permission = await Permission.create(key="book:borrow", name="Can borrow a book")
    await GroupPermission.create(group=group.id, permission=permission.id)
    await create_user(
        username=CUSTOMER_USERNAME,
        first_name="test",
        last_name="user",
        email=f"{CUSTOMER_USERNAME}@example.com",
        password_one=DEFAULT_PASSWORD,
        password_two=DEFAULT_PASSWORD,
        permission_group="customer",
    )


@pytest.fixture(scope="module")
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
        query=get_jwt_query,
        variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
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
        query=get_jwt_query,
        variables={"username": STAFF_USERNAME, "password": DEFAULT_PASSWORD},
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


async def test_get_tokens(turbulette_setup, tester, create_user):
    # Valid password
    response = await tester.assert_query_success(
        get_jwt_query,
        op_name="getJWT",
        variables={"username": CUSTOMER_USERNAME, "password": DEFAULT_PASSWORD},
    )

    assert response[1]["data"]["getJWT"]["accessToken"]
    assert response[1]["data"]["getJWT"]["refreshToken"]
    assert not response[1]["data"]["getJWT"]["errors"]

    # Invalid password
    response = await tester.assert_query_success(
        get_jwt_query,
        op_name="getJWT",
        variables={"username": CUSTOMER_USERNAME, "password": "invalid"},
    )

    assert not response[1]["data"]["getJWT"]["accessToken"]
    assert not response[1]["data"]["getJWT"]["refreshToken"]
    assert response[1]["data"]["getJWT"]["errors"]

    # User does not exist
    response = await tester.assert_query_success(
        get_jwt_query,
        op_name="getJWT",
        variables={"username": "invalid", "password": DEFAULT_PASSWORD},
    )
    assert not response[1]["data"]["getJWT"]["accessToken"]
    assert not response[1]["data"]["getJWT"]["refreshToken"]
    assert response[1]["data"]["getJWT"]["errors"]


async def test_refresh_jwt(turbulette_setup, create_user, get_user_tokens, tester):
    access_token, refresh_token = get_user_tokens

    query = """
            query refreshJWT {
                refreshJWT{
                    accessToken
                    errors
                }
            }
    """

    response = await tester.assert_query_success(query=query, jwt=refresh_token)

    assert response[1]["data"]["refreshJWT"]["accessToken"]

    response = await tester.assert_query_failed(query=query, jwt=access_token)

    assert "accessToken" not in response[1]["data"]

    response = await tester.assert_query_success(
        query=query, jwt=f"{refresh_token}__wrong__"
    )

    assert response[1]["data"]["refreshJWT"]["errors"]


async def test_login_required(
    turbulette_setup, create_user, get_user_tokens, false_access_jwt, tester
):
    response = await tester.assert_query_success(
        query=books_query, jwt=get_user_tokens[0]
    )

    assert response[1]["data"]["books"]["books"]

    response = await tester.assert_query_success(
        query=books_query, jwt=false_access_jwt
    )

    assert not response[1]["data"]["books"]["books"]


async def test_wrong_signature(turbulette_setup, tester, get_user_tokens):
    response = await tester.assert_query_success(
        query=books_query, jwt=get_user_tokens[0] + "wrong",
    )

    assert not response[1]["data"]["books"]["books"]


async def test_jwt_not_properly_formatted(turbulette_setup, tester, false_access_jwt):
    response = await tester.assert_query_failed(query=books_query, jwt="invalid")

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(query=books_query, jwt=" ")

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(
        query=books_query, headers={"authorization": f"{false_access_jwt}"},
    )

    assert not response[1]["data"]["books"]

    response = await tester.assert_query_failed(
        query=books_query, headers={"authorization": ""},
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
        jwt=false_refresh_jwt,
    )
    assert not response[1]["data"]["refreshJWT"]["errors"]
    assert response[1]["data"]["refreshJWT"]["accessToken"]


async def test_get_token_from_user(turbulette_setup, create_user, tester):
    from tests.app_1.models import BaseUser
    from turbulette.apps.auth import get_token_from_user

    user = await BaseUser.get_by_username(CUSTOMER_USERNAME)
    access_token = get_token_from_user(user)

    # Check token is valid
    response = await tester.assert_query_success(query=books_query, jwt=access_token,)

    assert not response[1]["data"]["books"]["errors"]
    assert response[1]["data"]["books"]["books"]


async def test_get_user_by_payload(
    turbulette_setup, create_user, get_user_tokens, false_access_jwt, tester
):
    from turbulette.apps.auth.core import get_user_by_payload, decode_jwt
    from turbulette.apps.auth.exceptions import JSONWebTokenError, UserDoesNotExists

    claims = decode_jwt(get_user_tokens[1])[1]
    user = await get_user_by_payload(claims)

    assert user.username == CUSTOMER_USERNAME

    # Invalid payload
    claims["sub"] = None

    with pytest.raises(JSONWebTokenError):
        user = await get_user_by_payload(claims)

    # Invalid user
    claims = decode_jwt(false_access_jwt)[1]
    with pytest.raises(UserDoesNotExists):
        user = await get_user_by_payload(claims)


async def test_create_user(turbulette_setup, tester, create_user_data):
    query = """
        mutation createUser(
            $username: String!
            $firstName: String!
            $lastName: String!
            $email:  String!
            $passwordOne: String!
            $passwordTwo: String!
        ) {
            createUser(input: {
                username: $username
                firstName: $firstName
                lastName: $lastName
                email: $email
                passwordOne: $passwordOne
                passwordTwo: $passwordTwo
            }) {
                user {
                    id
                    username
                    firstName
                    lastName
                    email
                }
                token
                errors
            }
        }
    """
    response = await tester.assert_query_success(
        query=query, op_name="createUser", variables={**create_user_data},
    )

    tester.assert_data_in_response(response, "createUser", create_user_data)

    # Test with invalid password
    create_user_data["passwordTwo"] = create_user_data["passwordOne"] + "different"
    response = await tester.assert_query_success(
        query=query, op_name="createUser", variables={**create_user_data},
    )

    assert response[1]["data"]["createUser"]["errors"]


async def test_staff_member(
    turbulette_setup, tester, create_staff_user, get_staff_tokens, get_user_tokens
):
    query = """
            mutation {
                addBook {
                    success
                    errors
                }
            }
    """

    response = await tester.assert_query_success(query=query, jwt=get_staff_tokens[0])

    assert not response[1]["data"]["addBook"]["errors"]

    response = await tester.assert_query_success(query=query, jwt=get_user_tokens[0])

    assert response[1]["data"]["addBook"]["errors"]
    assert not response[1]["data"]["addBook"]["success"]


async def test_permission(
    turbulette_setup,
    tester,
    create_user_data,
    create_staff_user,
    get_staff_tokens,
    get_user_tokens,
):
    query = """
            mutation {
                borrowBook {
                    success
                    errors
                }
            }
    """

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

    response = await tester.assert_query_success(query=query, jwt=get_user_tokens[0])

    assert not response[1]["data"]["borrowBook"]["errors"]
    assert response[1]["data"]["borrowBook"]["success"]

    # The staff user has not `book:borrow` permission
    response = await tester.assert_query_success(query=query, jwt=get_staff_tokens[0])

    assert response[1]["data"]["borrowBook"]["errors"]
    assert not response[1]["data"]["borrowBook"]["success"]

    response = await tester.assert_query_success(
        query=query,
        headers={"authorization": f"JWT {get_token_from_user(user_no_group)}"},
    )

    assert response[1]["data"]["borrowBook"]["errors"]
    assert not response[1]["data"]["borrowBook"]["success"]


async def test_access_token_required(turbulette_setup, tester, get_user_tokens):
    response = await tester.assert_query_success(
        query="""
            query {
                exclusiveBooks {
                    books {
                        title
                        author
                    }
                    errors
                }
            }
        """,
        jwt=get_user_tokens[0],
    )

    assert not response[1]["data"]["exclusiveBooks"]["errors"]
