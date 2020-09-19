from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from turbulette.core.utils import is_query
from .decorators import access_token_required, fresh_token_required, scope_required


class AccessTokenRequiredDirective(SchemaDirectiveVisitor):
    name = "access_token_required"

    def visit_field_definition(
        self, field, object_type
    ):  # pylint: disable=unused-argument
        original_resolver = field.resolve or default_field_resolver

        @access_token_required
        async def resolve_login_required(obj, info, claims, **kwargs):
            return await original_resolver(obj, info, claims=claims, **kwargs)

        field.resolve = resolve_login_required
        return field


class FreshTokenRequiredDirective(SchemaDirectiveVisitor):
    name = "fresh_token_required"

    def visit_field_definition(
        self, field, object_type
    ):  # pylint: disable=unused-argument
        original_resolver = field.resolve or default_field_resolver

        @fresh_token_required
        async def resolve_fresh_token_required(obj, info, claims, **kwargs):
            return await original_resolver(obj, info, claims=claims, **kwargs)

        field.resolve = resolve_fresh_token_required
        return field


class ScopeDirective(SchemaDirectiveVisitor):
    name = "scope"

    def visit_field_definition(
        self, field, object_type
    ):  # pylint: disable=unused-argument
        original_resolver = field.resolve or default_field_resolver

        @scope_required
        async def resolve_scope(obj, info, claims, **kwargs):
            if is_query(info):
                return await original_resolver(obj, info, claims=claims, **kwargs)
            return original_resolver(obj, info, **kwargs)

        field.resolve = resolve_scope
        return field
