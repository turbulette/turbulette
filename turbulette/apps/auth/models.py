import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from turbulette.db import Model
from .exceptions import UserDoesNotExists


class AbstractUser:
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    date_joined = Column(DateTime(), default=datetime.datetime.utcnow())
    first_name = Column(String)
    last_name = Column(String)
    is_staff = Column(Boolean, default=False, nullable=False)
    permission_role = Column(Integer, ForeignKey("auth_role.id"))

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
