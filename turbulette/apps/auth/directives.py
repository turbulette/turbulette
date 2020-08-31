from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from .decorators import scope_required, access_token_required


class LoginRequiredDirective(SchemaDirectiveVisitor):
    name = "access_token_required"

    def visit_field_definition(
        self, field, object_type
    ):  # plyint: disable=unused-argument
        original_resolver = field.resolve or default_field_resolver

        @access_token_required
        async def resolve_login_required(obj, info, user, **kwargs):
            return await original_resolver(obj, info, user, **kwargs)

        field.resolve = resolve_login_required
        return field


class ScopeDirective(SchemaDirectiveVisitor):
    name = "scope"

    def visit_field_definition(
        self, field, object_type
    ):  # plyint: disable=unused-argument
        original_resolver = field.resolve or default_field_resolver

        @scope_required(
            permissions=self.args.get("permissions"), is_staff=self.args.get("is_staff")
        )
        async def resolve_scope(obj, info, user, **kwargs):
            return await original_resolver(obj, info, user, **kwargs)

        field.resolve = resolve_scope
        return field
