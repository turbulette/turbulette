import json
from pathlib import Path

from ariadne.types import GraphQLResolveInfo

from turbulette.conf import settings

from .policy import PolicyType

# Base policy object
policy = PolicyType()


def get_policy_config():
    """Get policy either from file or memory."""
    if not hasattr(settings, "POLICY"):
        with open(Path(settings.POLICY_CONFIG)) as file:
            config = json.load(file)
            settings.configure(POLICY=config)
    return settings.POLICY


async def authorized(claims: dict, info: GraphQLResolveInfo) -> bool:
    """Evaluate authorization policies with the JWT claims and the query infos.

    Args:
        claims (dict): JWT claims
        info (GraphQLResolveInfo): Query infos

    Returns:
        bool: True if authorized, False otherwise
    """
    policies = get_policy_config()
    policies = await policy.involved(claims, policies, info)
    if not policies:  # pragma: no cover ### can't cover both all policy types and none
        return False
    valid_policies = await policy.with_valid_conditions(claims, policies, info)
    if (
        not valid_policies
    ):  # pragma: no cover ### can't cover both all context types and none
        return False
    applied_policies = policy.apply(info, valid_policies)
    authorized_ = bool(applied_policies) and all(applied_policies)
    return authorized_
