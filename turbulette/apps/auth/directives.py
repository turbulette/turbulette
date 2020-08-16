from ariadne import SchemaDirectiveVisitor
from graphql import default_field_resolver
from .decorators import login_required, staff_member_required, permission_required


class LoginRequiredDirective(SchemaDirectiveVisitor):
    name = "login_required"

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        @login_required
        async def resolve_login_required(obj, info, user, **kwargs):
            return await original_resolver(obj, info, user, **kwargs)
        field.resolve = resolve_login_required
        return field


class StaffMemberRequiredDirective(SchemaDirectiveVisitor):
    name = "staff_member_required"

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        @staff_member_required
        async def resolve_is_staff(obj, info, user, **kwargs):
            return await original_resolver(obj, info, user, **kwargs)

        field.resolve = resolve_is_staff
        return field


class ScopeDirective(SchemaDirectiveVisitor):
    name = "scope"

    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver

        @permission_required(permissions=self.args.get("permissions"))
        async def resolve_scope(obj, info, user, **kwargs):
            return await original_resolver(obj, info, user, **kwargs)

        field.resolve = resolve_scope
        return field
