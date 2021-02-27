"""Base models to store users, permissions and roles."""

import datetime
from typing import List, Optional, Type

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
)

from turbulette.apps import auth
from turbulette.conf import settings
from turbulette.db.database import Model, get_tablename
from turbulette.db.exceptions import DoesNotExist


def auth_user_tablename() -> str:
    """Get the auth table name from settings or generate it."""
    return settings.AUTH_USER_MODEL_TABLENAME or get_tablename(
        settings.AUTH_USER_MODEL.rsplit(".", 3)[-3],
        settings.AUTH_USER_MODEL.split(".")[-1],
    )


class Permission(Model):
    """A permission specify a certain right a user has."""

    id = Column(Integer, primary_key=True)
    """Primary key Required (`nullable=False`) and must be"""

    name = Column(String, nullable=False)
    """Required (`nullable=False`). Should be human readable."""

    key = Column(String, nullable=False, unique=True)
    """Required (`nullable=False`), and must be unique.
        Used to identify the permission in JWT.
    """

    def __repr__(self, key: str = None):
        """Use the key to identify the Permission object."""
        return super().__repr__(self.key)


class RolePermission(Model):
    """Simple table to link roles and permissions."""

    role = Column(Integer, primary_key=True)
    """Foreign key to the linked role. Part of the primary key."""

    permission = Column(Integer, primary_key=True)
    """Foreign key to the linked permission. Part of the primary key."""

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
    """A role is a permission group to which users belong."""

    id = Column(Integer, primary_key=True)
    """Primary key Required (`nullable=False`) and must be"""

    name = Column(String, nullable=False, unique=True)
    """Required (`nulllable=False`) and must be unique Must be unique.
        Used to identify the role in JWT.
    """

    def __init__(self, **values):
        super().__init__(**values)
        self._permissions = []

    def __repr__(self, key: str = None):
        """Use the name to identify the Role object."""
        return super().__repr__(self.name)

    @property
    def permissions(self) -> list:
        return self._permissions

    @permissions.setter  # type: ignore [attr-defined]
    def add_permission(self, permission):
        self._permissions.append(permission)


class UserRole(Model):
    """Link users to roles."""

    user = Column(
        Integer,
        ForeignKey(auth_user_tablename() + ".id"),
        primary_key=True,
    )
    """Foreign key to the user defined by `AUTH_USER_MODEL` setting.
        part of the primary key.
    """
    role = Column(Integer, ForeignKey("auth_role.id"), primary_key=True)
    """Foreign key to the associated role. Part of the primary key."""

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
    """Abstract user class serving as a base to implement a concrete user model."""

    id = Column(Integer, primary_key=True)
    """Primary key Required (`nullable=False`) and must be"""

    email = Column(String, nullable=False, unique=True)
    """Required (`nullable=False`) and must be unique."""

    username = Column(String, unique=True)
    """Required (`nullable=False`) and must be unique.
        username is used to create user JWT and retrieve roles and.
    """

    hashed_password = Column(String, nullable=False)
    """Stores the hashed user password. Every time the user logs in,
        the hash of the provided password is compared against `hashed_password`.
        Hash algorithm is defined by the `HASH_ALGORITHM` setting.
    """

    date_joined = Column(DateTime(), default=datetime.datetime.utcnow())
    """Stores the current datetime (UTC) when the user is created in the database."""

    first_name = Column(String)
    """Optional (`nullable=True`)"""

    last_name = Column(String)
    """Optional (`nullable=True`)"""

    is_staff = Column(Boolean, default=False, nullable=False)
    """Indicates if the user is a "staff" member.
        Staff is a special role stored in database as a convenience.
        It's up to you to define what's "staff" means in your use case.
    """
    # Used as the unique identifier.
    USERNAME_FIELD = "username"

    def __repr__(self):
        """Identify concrete user by their `USERNAME` field.

        Only work if it's lower than __repr__ of `Model`
        in the MRO of the concrete user class.

        example :

        This will correctly output `<ConcreteUser: username>`:

            class ConcreteUser(AbstractUser, Model):
                ...

        While this will make the __repr__ method of `Model` to be used:

            class ConcreteUser(Model, AbstractUser):
                ...
        """
        return super().__repr__(self.get_username())

    async def _get_object(
        self,
        obj_class: Model,
        key: str,
        obj: Type[Model] = None,
        key_value: str = None,
    ) -> Model:
        """Get model objects based on instance or a specific column."""
        obj_ = None
        if obj:
            obj_ = obj
        elif key_value:
            obj_ = await obj_class.query.where(
                getattr(obj_class, key) == key_value
            ).gino.first()
            if not obj_:
                raise DoesNotExist(self)
        if not obj_:
            raise Exception(
                f"You must provide either a {obj_class.__name__} object or a {key}"
            )
        return obj_

    def get_username(self) -> str:
        """Return username of this user using `USERNAME_FIELD` attribute.

        Returns:
            str: The username
        """
        return str(getattr(self, self.USERNAME_FIELD))

    @classmethod
    async def get_by_username(cls, username: str):
        """Get the user object from its `username`.

        Args:
            username: username

        Raises:
            DoesNotExist: Raised if no user match the given username

        Returns:
            User: Returns a user object of type defined by `AUTH_USER_MODEL`
        """
        user = await cls.query.where(  # type: ignore [attr-defined] # pylint: disable=no-member
            getattr(cls, cls.USERNAME_FIELD) == username
        ).gino.first()
        if not user:
            raise DoesNotExist(cls)
        return user

    @classmethod
    async def set_password(cls, username: str, password: str) -> None:
        """Changes user password.

        The new password will be hashed using the hash algorithm defined
        by the `HASH_ALGORITHM` setting, and the resulting hash stored
        in the `hashed_password` column.

        Args:
            username (str): Identify the user for whom the password needs to be updated
            password (str): The new password
        """
        user = await cls.get_by_username(username)
        hashed_password = auth.get_password_hash(password)
        await user.update(hashed_password=hashed_password).apply()

    async def get_perms(self) -> List[Permission]:
        """Get permissions this user has through their roles.

        Returns:
            A list of [Permission][turbulette.apps.auth.models.Permission]
        """
        query = UserRole.join(Role).join(RolePermission).join(Permission).select()

        return (
            await query.gino.load(Permission.load())
            .query.where(UserRole.user == self.id)
            .gino.all()
        )

    async def get_roles(self) -> List[Role]:
        """Get all the roles to which the user belongs.

        Returns:
            A list of [Role][turbulette.apps.auth.models.Role]
        """
        query = UserRole.join(Role).select()
        return (
            await query.gino.load(Role.load())
            .query.where(UserRole.user == self.id)
            .gino.all()
        )

    async def add_role(self, role: Optional[Role] = None, name: Optional[str] = None):
        """Adds a role to the user.

        The role can be given either as a
        [Role][turbulette.apps.auth.models.Role] object, or by its name.

        Args:
            role: The [Role][turbulette.apps.auth.models.Role] to add.
            name: Name of the role to add.
        """
        role_ = await self._get_object(Role, "name", role, name)
        await UserRole.create(user=self.id, role=role_.id)

    async def remove_role(
        self, role: Optional[Role] = None, name: Optional[str] = None
    ):
        """Removes a user role.

        The role can be given either as a
        [Role][turbulette.apps.auth.models.Role] object, or by its name.

        Args:
            role: [Role][turbulette.apps.auth.models.Role] to remove.
            name: Name of the role to remove.
        """
        role_ = await self._get_object(Role, "name", role, name)
        await UserRole.delete.where(
            UserRole.user == self.id and UserRole.role == role_.id
        ).gino.status()

    async def role_perms(self) -> List[Role]:
        """Loads user roles and permissions.

        Returns:
            List of [Role][turbulette.apps.auth.models.Role] an their permissions
        """
        query = UserRole.join(Role).join(RolePermission).join(Permission).select()
        return (
            await query.where(UserRole.user == self.id)
            .gino.load(Role.distinct(Role.id).load(add_permission=Permission.load()))
            .query.gino.all()
        )
