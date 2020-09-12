import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

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


class Role(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self, key: str = None):
        """Use the name to identify the Role object."""
        return super().__repr__(self.name)


class Permission(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False, unique=True)

    def __repr__(self, key: str = None):
        """Use the key to identify the Permission object."""
        return super().__repr__(self.key)


class RolePermission(Model):
    id = Column(Integer, primary_key=True)
    role = Column(Integer, ForeignKey("auth_role.id"), nullable=False)
    permission = Column(Integer, ForeignKey("auth_permission.id"), nullable=False)

    def __repr__(self, key: str = None):
        """Use the role and permission to identify the RolePermission object."""
        return super().__repr__(f"role: {self.role}, permission: {self.permission}")


class UserPermission(Model):
    """Link users to permissions.

    This allow to control user's permissions on a more granular level
    by giving additional permissions to specific users, in addition to
    those already granted by roles.

    Note that we dynamically generate `AUTH_USER_MODEL` table name to reference it
    in the `ForeignKey`, so the alembic migration won't work
    if `__tablename__` is set on `AUTH_USER_MODEL`.
    """

    id = Column(Integer, primary_key=True)
    user = Column(
        Integer,
        ForeignKey(auth_user_tablename() + ".id"),
        nullable=False,
    )
    permission = Column(Integer, ForeignKey("auth_permission.id"), nullable=False)


class UserRole(Model):
    """Link users to roles.

    Note that we dynamically generate `AUTH_USER_MODEL` table name to reference it
    in the `ForeignKey`, so the alembic migration won't work
    if `__tablename__` is set on `AUTH_USER_MODEL`.
    """

    id = Column(Integer, primary_key=True)
    user = Column(
        Integer,
        ForeignKey(auth_user_tablename() + ".id"),
        nullable=False,
    )
    role = Column(Integer, ForeignKey("auth_role.id"), nullable=False)
