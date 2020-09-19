import json
from pathlib import Path
from typing import Dict, List
from ariadne.types import GraphQLResolveInfo
from turbulette.conf import settings
from turbulette.core.cache import cache
from . import user_model


def c_claim(claims: Dict[str, str], statement: dict) -> bool:
    if not claims.get(statement["claim"]):
        return False
    return set(claims[statement["claim"]]).issubset(statement["includes"])


def c_is_claim_present(claims: Dict[str, str], statement: dict) -> bool:
    return statement["is_claim_present"] in claims


CONDITIONS = {
    "claim": c_claim,
    "is_claim_present": c_is_claim_present,
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
        if "condition" not in policy or all(
            CONDITIONS[list(st.keys())[0]](claims, st) for st in policy["conditions"]
        ):
            valid_policies.append(policy)
    return valid_policies


def match(key: str, values: dict, info: GraphQLResolveInfo) -> bool:
    match_ = False
    if key == info.parent_type.name.lower() and info.field_name in values["fields"]:
        if "query" in values:
            root_field = info.path

            while root_field.prev is not None:
                root_field = root_field.prev

            for pattern in values["query"]:
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
        if "allow" in policy:
            if any(match(key, val, info) for key, val in policy["allow"].items()):
                allowed = True
        if "deny" in policy:
            if any(match(key, val, info) for key, val in policy["deny"].items()):
                allowed = False
        if allowed is not None:
            applied_apolicies.append(allowed)
    return applied_apolicies


async def is_involved(claims: dict, statement: str) -> bool:
    involved = False
    if statement == "*":
        involved = True

    elif statement == "staff":
        involved = "_staff" in claims["scopes"]

    else:
        type_key, type_val = statement.split(":", 1)

        if type_key == "role" and type_val in claims["scopes"]:
            involved = True

        elif type_key == "perm":
            for role in claims["scopes"]:
                if not role.startswith("_"):
                    cached_role = await cache.get(role)
                    if any(type_val == perm["key"] for perm in cached_role):
                        involved = True
                        break

        elif type_key == "user":
            involved = claims["sub"] == type_val
    return involved


async def involved_policies(claims: dict, policies: List[dict]):
    res = []
    for policy in policies:
        for statement in policy["principal"]:
            if await is_involved(claims, statement):
                res.append(policy)
    return res


async def has_scope_(claims: dict, info: GraphQLResolveInfo) -> bool:
    policies = get_policy_config()
    policies = await involved_policies(claims, policies)
    if not policies:
        return False
    valid_ctx = ctx_is_valid(claims, policies)
    if not valid_ctx:
        return False
    applied_policies = authorize(info, valid_ctx)
    authorized = bool(applied_policies) and all(applied_policies)
    return authorized
