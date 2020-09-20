import json
from pathlib import Path
from typing import Dict, List
from ariadne.types import GraphQLResolveInfo
from turbulette.conf import settings
from turbulette.core.cache import cache
from .core import STAFF_SCOPE

KEY_PRINCIPAL = "principal"
KEY_CONDITIONS = "conditions"
KEY_ALLOW_FIELDS = "fields"
KEY_ALLOW_QUERY = "query"
KEY_ALLOW = "allow"
KEY_DENY = "deny"


def c_claim(claims: Dict[str, str], statement: dict) -> bool:
    return bool(claims.get(statement["claim"])) and all(
        inc in claims[statement["claim"]] for inc in statement["includes"]
    )


def c_is_claim_present(claims: Dict[str, str], statement: dict) -> bool:
    return statement["is_claim_present"] in claims


async def p_has_perm(val: str, claims: dict) -> bool:
    involved = False
    for role in claims["scopes"]:
        if not role.startswith("_"):
            cached_role = await cache.get(role)
            if any(val == perm["key"] for perm in cached_role):
                involved = True
                break
    return involved


async def p_is_staff(val: str, claims: dict) -> bool:  # pylint: disable=unused-argument
    return STAFF_SCOPE in claims["scopes"]


async def p_has_role(val: str, claims: dict) -> bool:
    return val in claims["scopes"]


async def p_is_user(val: str, claims: dict) -> bool:
    return claims["sub"] == val


async def p_all(val: str, claims: dict):  # pylint: disable=unused-argument
    return True


CONDITIONS = {
    "claim": c_claim,
    "is_claim_present": c_is_claim_present,
}

PRINCIPAL_PATTERNS = {
    "*": p_all,
    "staff": p_is_staff,
    "role": p_has_role,
    "user": p_is_user,
    "perm": p_has_perm,
}


def get_policy_config():
    """Get policy either from file or memory."""
    if not hasattr(settings, "POLICY"):
        with open(Path(settings.POLICY_CONFIG)) as file:
            config = json.load(file)
            settings.configure(POLICY=config)
    return settings.POLICY


def ctx_is_valid(claims: Dict[str, str], policies: List[dict]) -> List[dict]:
    """Given a list of policies, return only those with valid conditions."""
    valid_policies = []
    for policy in policies:
        if KEY_CONDITIONS not in policy or all(
            CONDITIONS[list(st.keys())[0]](claims, st) for st in policy[KEY_CONDITIONS]
        ):
            valid_policies.append(policy)
    return valid_policies


def match(key: str, values: dict, info: GraphQLResolveInfo) -> bool:
    match_ = False
    if (
        key == info.parent_type.name.lower()
        and info.field_name in values[KEY_ALLOW_FIELDS]
    ):
        if KEY_ALLOW_QUERY in values:
            root_field = info.path

            while root_field.prev is not None:
                root_field = root_field.prev

            for pattern in values[KEY_ALLOW_QUERY]:
                if pattern.endswith("*"):
                    match_ = str(root_field.key).startswith(pattern.split("*")[0])
                elif pattern.startswith("*"):
                    match_ = str(root_field.key).endswith(pattern.split("*")[1])
                else:
                    match_ = str(root_field.key) == pattern
                if match_:
                    break
        else:
            match_ = True
    return match_


def authorize(info: GraphQLResolveInfo, policies: List[dict]) -> List[bool]:
    applied_apolicies = []
    for policy in policies:
        allowed = None
        if KEY_ALLOW in policy:
            if any(match(key, val, info) for key, val in policy[KEY_ALLOW].items()):
                allowed = True
        if KEY_DENY in policy:
            if any(match(key, val, info) for key, val in policy[KEY_DENY].items()):
                allowed = False
        if allowed is not None:
            applied_apolicies.append(allowed)
    return applied_apolicies


async def involved_policies(claims: dict, policies: List[dict]):
    res = []
    for policy in policies:
        for statement in policy[KEY_PRINCIPAL]:
            parsed = statement.split(":", 1)
            val = parsed[0] if len(parsed) == 1 else parsed[1]
            if await PRINCIPAL_PATTERNS[parsed[0]](val, claims):
                res.append(policy)
    return res


async def has_scope_(claims: dict, info: GraphQLResolveInfo) -> bool:
    policies = get_policy_config()
    policies = await involved_policies(claims, policies)
    if not policies:  # pragma: no cover ### can't cover both all policy types and none
        return False
    valid_ctx = ctx_is_valid(claims, policies)
    if (
        not valid_ctx
    ):  # pragma: no cover ### can't cover both all context types and none
        return False
    applied_policies = authorize(info, valid_ctx)
    authorized = bool(applied_policies) and all(applied_policies)
    return authorized
