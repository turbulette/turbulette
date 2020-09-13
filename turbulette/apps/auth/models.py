import datetime
from typing import Any, List, Optional, Tuple, Type, Union
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    ForeignKeyConstraint,
)

from turbulette.apps import auth
from turbulette.conf import settings
from turbulette.db import Model, get_tablename

from .exceptions import UserDoesNotExists


def auth_user_tablename() -> str:
    """Get the auth table name from settings or generate it."""
    return settings.AUTH_USER_MODEL_TABLENAME or get_tablename(
        settings.AUTH_USER_MODEL.rsplit(".", 3)[-3],
        settings.AUTH_USER_MODEL.split(".")[-1],
    )


class Permission(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False, unique=True)

    def __repr__(self, key: str = None):
        """Use the key to identify the Permission object."""
        return super().__repr__(self.key)


class RolePermission(Model):
    role = Column(Integer, primary_key=True)
    permission = Column(Integer, primary_key=True)

    permission_fk = ForeignKeyConstraint(
        ["permission"],
        ["auth_permission.id"],
        name="permission_fk",
    )

    role_fk = ForeignKeyConstraint(
        ["role"],
        ["auth_role.id"],
        name="role_fk",
    )

    def __repr__(self, key: str = None):
        """Use the role and permission to identify the RolePermission object."""
        return super().__repr__(f"role: {self.role}, permission: {self.permission}")


class Role(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self, key: str = None):
        """Use the name to identify the Role object."""
        return super().__repr__(self.name)


class UserPermission(Model):
    """Link users to permissions.

    This allow to control user's permissions on a more granular level
    by giving additional permissions to specific users, in addition to
    those already granted by roles.

    Note that we dynamically generate `AUTH_USER_MODEL` table name to reference it
    in the `ForeignKey`, so the alembic migration won't work
    if `__tablename__` is set on `AUTH_USER_MODEL`.
    """

    user = Column(
        Integer,
        ForeignKey(auth_user_tablename() + ".id"),
        primary_key=True,
    )
    permission = Column(Integer, ForeignKey("auth_permission.id"), primary_key=True)

    user_fk = ForeignKeyConstraint(
        ["user"],
        [auth_user_tablename() + ".id"],
        name="user_fk",
    )

    permission_fk = ForeignKeyConstraint(
        ["permission"],
        ["auth_permission.id"],
        name="permission_fk",
    )


class UserRole(Model):
    """Link users to roles.

    Note that we dynamically generate `AUTH_USER_MODEL` table name to reference it
    in the `ForeignKey`, so the alembic migration won't work
    if `__tablename__` is set on `AUTH_USER_MODEL`.
    """

    user = Column(
        Integer,
        ForeignKey(auth_user_tablename() + ".id"),
        primary_key=True,
    )
    role = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)

    user_fk = ForeignKeyConstraint(
        ["user"],
        [auth_user_tablename() + ".id"],
        name="user_fk",
    )

    role_fk = ForeignKeyConstraint(
        ["role"],
        ["auth_role.id"],
        name="role_fk",
    )


class AbstractUser:
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    date_joined = Column(DateTime(), default=datetime.datetime.utcnow())
    first_name = Column(String)
    last_name = Column(String)
    is_staff = Column(Boolean, default=False, nullable=False)

    # Used as the unique identifier.
    USERNAME_FIELD = "username"

    def __repr__(self):
        """Will work only it's lower than __repr__ of `Model` in the MRO of the concrete user class.

        example :

        This will correctly output `<ConcreteUser: username>`

                class ConcreteUser(AbstractUser, Model):
                    ...

        While this will make the __repr__ method of `Model` to be used

                class ConcreteUser(Model, AbstractUser):
                    ...
        """
        return super().__repr__(self.get_username())

    async def _get_object(
        self,
        obj_class: Model,
        key: str,
        obj: Type[Model] = None,
        identifier: str = None,
    ) -> Model:
        """Lazy getter for model objects."""
        obj_ = None
        if obj:
            obj_ = obj
        elif identifier:
            obj_ = await obj_class.query.where(
                getattr(obj_class, key) == identifier
            ).gino.first()
            if not obj_:
                raise Exception(f"{obj_class.__name__} does not exists")
        if not obj_:
            raise Exception(
                f"You must provide either a {obj_class.__name__} object or a {key}"
            )
        return obj_

    def get_username(self) -> str:
        return str(getattr(self, self.USERNAME_FIELD))

    @classmethod
    async def get_by_username(cls, username: str):
        user = await cls.query.where(  # type: ignore [attr-defined] # pylint: disable=no-member
            getattr(cls, cls.USERNAME_FIELD) == username
        ).gino.first()
        if not user:
            raise UserDoesNotExists
        return user

    @classmethod
    async def set_password(cls, username: str, password: str):
        user = await cls.get_by_username(username)
        hashed_password = auth.get_password_hash(password)
        await user.update(hashed_password=hashed_password).apply()

    async def get_role_perms(self) -> List[Permission]:
        """Get permissions that this user has through their roles."""
        query = UserRole.join(Role).join(RolePermission).join(Permission).select()

        return (
            await query.gino.load(Permission.load())
            .query.where(UserRole.user == self.id)
            .gino.all()
        )

    async def get_perms(self) -> List[Permission]:
        """Get all custom user permissions, not belonging to the user roles."""
        query = UserPermission.join(Permission).select()

        return (
            await query.gino.load(Permission.load())
            .query.where(UserPermission.user == self.id)
            .gino.all()
        )

    async def get_roles(self) -> List[Role]:
        """Get all the roles to which the user belongs."""
        query = UserRole.join(Role).select()
        return (
            await query.gino.load(Role.load())
            .query.where(UserRole.user == self.id)
            .gino.all()
        )

    async def add_role(
        self, role: Optional[Permission] = None, name: Optional[str] = None
    ):
        """Add a role to the user."""
        role_ = await self._get_object(Role, "name", role, name)
        await UserRole.create(user=self.id, role=role_.id)

    async def remove_role(
        self, role: Optional[Permission] = None, name: Optional[str] = None
    ):
        """Remove a user role."""
        role_ = await self._get_object(Role, "name", role, name)
        await UserRole.delete.where(
            UserRole.user == self.id and UserRole.role == role_.id
        ).gino.status()

    async def add_perm(
        self, permission: Optional[Permission] = None, key: Optional[str] = None
    ):
        """Add a permission to the user."""
        permission_ = await self._get_object(Permission, "key", permission, key)
        await UserPermission.create(user=self.id, permission=permission_.id)

    async def remove_perm(
        self, permission: Optional[Permission] = None, key: Optional[str] = None
    ):
        """Remove a permission to the user."""
        permission_ = await self._get_object(Permission, "key", permission, key)
        await UserPermission.delete.where(
            UserPermission.user == self.id
            and UserPermission.permission == permission_.id
        ).gino.status()
