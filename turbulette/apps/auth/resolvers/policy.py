from turbulette.type import Claims
from turbulette.apps.auth.core import STAFF_SCOPE
from turbulette.core.cache import cache
from turbulette.apps.auth import policy


@policy.condition("claim")
async def claim(statement: dict, claims: Claims) -> bool:
    return bool(claims.get(statement["claim"])) and all(
        inc in claims[statement["claim"]] for inc in statement["includes"]
    )


@policy.condition("is_claim_present")
async def is_claim_present(statement: dict, claims: Claims) -> bool:
    return statement["is_claim_present"] in claims


@policy.principal("perm")
async def has_perm(val: str, claims: Claims) -> bool:
    involved = False
    for role in claims["scopes"]:
        if not role.startswith("_"):
            cached_role = await cache.get(role)
            if any(val == perm["key"] for perm in cached_role):
                involved = True
                break
    return involved


@policy.principal("staff")
async def is_staff(val: str, claims: Claims) -> bool:  # pylint: disable=unused-argument
    return STAFF_SCOPE in claims["scopes"]


@policy.principal("role")
async def has_role(val: str, claims: Claims) -> bool:
    return val in claims["scopes"]


@policy.principal("user")
async def is_user(val: str, claims: Claims) -> bool:
    return claims["sub"] == val


@policy.principal("*")
async def anybody(val: str, claims: Claims):  # pylint: disable=unused-argument
    return True
