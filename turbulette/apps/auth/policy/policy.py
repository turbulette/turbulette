from typing import Callable, Dict, List

from graphql.pyutils import Path
from graphql.type.definition import GraphQLResolveInfo

from turbulette.type import Claims, ConditionResolver, Policy, PrincipalResolver

from .constants import (
    KEY_ALLOW,
    KEY_ALLOW_FIELDS,
    KEY_ALLOW_QUERY,
    KEY_CONDITIONS,
    KEY_DENY,
    KEY_PRINCIPAL,
)


class PolicyType:
    """Store policy resolvers and handle core logic to apply policies.

    Policy evaluation follows the principle of least privilege :
    Access is authorized if *any* policy allows it, and *no* policy denies it
    """

    _principals: Dict[str, PrincipalResolver]
    _conditions: Dict[str, ConditionResolver]

    def __init__(self):
        self._principals = {}
        self._conditions = {}

    def _parse_query_string(self, pattern: str, field: Path) -> bool:
        match = False
        if pattern.endswith("*"):
            match = str(field.key).startswith(pattern.split("*")[0])
        elif pattern.startswith("*"):
            match = str(field.key).endswith(pattern.split("*")[1])
        else:
            match = str(field.key) == pattern
        return match

    def _match(self, type_: str, values: dict, info: GraphQLResolveInfo) -> bool:
        """Check if the current query match any of the given patterns.

        Args:
            key (str): GraphQL type to check for matches

            values (dict): Matching filters
                - fields : Specify fields to match
                - query : Specify which query/mutation to match

            info (GraphQLResolveInfo): GraphQL infos for the current query

        Returns:
            bool: True if it match False otherwise
        """
        match_ = False
        if (
            type_ == info.parent_type.name.lower()
            and info.field_name in values[KEY_ALLOW_FIELDS]
        ):
            if KEY_ALLOW_QUERY in values:
                root_field = info.path

                while root_field.prev is not None:
                    root_field = root_field.prev

                match_ = any(
                    self._parse_query_string(pattern, root_field)
                    for pattern in values[KEY_ALLOW_QUERY]
                )

            else:
                match_ = True
        return match_

    def principal(self, key: str) -> Callable[[Callable], PrincipalResolver]:
        """Decorator to add principal resolver.

        Args:
            key (str): Principal key to use in the policy config
        """
        if not isinstance(key, str):
            raise ValueError(
                "policy principal decorator should be passed a key: "
                '@policy.principal("foo")'
            )
        return self._create_register_principal(key)

    def condition(self, key: str) -> Callable[[Callable], ConditionResolver]:
        """Decorator to add a condition resolver.

        Args:
            key (str): Condition key to use in the policy config
        """
        if not isinstance(key, str):
            raise ValueError(
                "policy condition decorator should be passed a key: "
                '@policy.condition("bar")'
            )
        return self._create_register_conditions(key)

    def _create_register_principal(
        self, name: str
    ) -> Callable[[Callable], PrincipalResolver]:
        def register_resolver(func: Callable) -> Callable:
            self._principals[name] = func
            return func

        return register_resolver

    def _create_register_conditions(
        self, name: str
    ) -> Callable[[Callable], ConditionResolver]:
        def register_resolver(func: Callable) -> Callable:
            self._conditions[name] = func
            return func

        return register_resolver

    async def involved(
        self, claims: Claims, policies: List[Policy], info: GraphQLResolveInfo
    ) -> List[Policy]:
        """Given a list of policies, return only those where one of the principal patterns match.

        All principal resolvers will be tested. For a policy to be involved,
        at least one of the resolvers must return True.

        Args:
            claims (Claims): Current JWT claims
            policies (List[Policy]): The policy list to filter

        Returns:
            List[Policy]: Involved policies
        """
        res = []
        for policy in policies:
            for statement in policy[KEY_PRINCIPAL]:
                parsed = statement.split(":", 1)
                val = parsed[0] if len(parsed) == 1 else parsed[1]
                if await self._principals[parsed[0]](val, claims, info):
                    res.append(policy)
                    break
        return res

    async def with_valid_conditions(
        self, claims: Claims, policies: List[Policy], info: GraphQLResolveInfo
    ) -> List[Policy]:
        """Given a list of policies, return only those with valid conditions.

        All condition resolvers will be tested. For a policy to have valid conditions,
        all resolvers must return True.

        Args:
            claims (Claims): Current JWT claims
            policies (List[Policy]): The policy to filter

        Returns:
            List[Policy]: Policies where all conditions are valid
        """
        valid_policies = []
        for policy in policies:
            if KEY_CONDITIONS not in policy:
                valid_policies.append(policy)
            else:
                for statement, val in policy[KEY_CONDITIONS].items():
                    if not await self._conditions[statement](val, claims, info):
                        break
                else:
                    valid_policies.append(policy)
        return valid_policies

    def _apply(self, info: GraphQLResolveInfo, key: str, policy: Policy) -> bool:
        """Return True if any of the policy allow statements match.

        Args:
            info (GraphQLResolveInfo): GraphQL infos for the current query
            key (str): Should be either `KEY_ALLOW` or `KEY_DENY`
            policy (Policy): The policy to check

        Returns:
            bool: [description]
        """
        return any(self._match(key, val, info) for key, val in policy[key].items())

    def apply(self, info: GraphQLResolveInfo, policies: List[Policy]) -> List[bool]:
        """Given a list of policies, return whether not each of them allow or deny the access.

        Args:
            info (GraphQLResolveInfo): GraphQL infos for the current query
            policies (List[Policy]): Policies to apply

        Returns:
            List[bool]: A list of allow/deny booleans for each policies
        """
        applied_apolicies = []
        for policy_ in policies:
            allowed = None
            if KEY_ALLOW in policy_ and self._apply(info, KEY_ALLOW, policy_):
                allowed = True
            if KEY_DENY in policy_ and self._apply(info, KEY_DENY, policy_):
                allowed = False
            if allowed is not None:
                applied_apolicies.append(allowed)
        return applied_apolicies
