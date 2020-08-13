import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)

from turbulette.db import Model


class AbstractUser:
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    date_joined = Column(DateTime(), default=datetime.datetime.utcnow())
    first_name = Column(String)
    last_name = Column(String)
    is_staff = Column(Boolean, default=False, nullable=False)
    permission_group = Column(Integer, ForeignKey("auth_group.id"))

    # Used as the unique identifier.
    USERNAME_FIELD = "username"

    def __repr__(self):
        return f"{self.get_username()}"


    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)


    @classmethod
    async def get_by_username(cls, username: str):
        return await cls.query.where(getattr(cls, cls.USERNAME_FIELD) == username).gino.first()


class Group(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"{self.name}"


class Permission(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"{self.key}"


class GroupPermission(Model):
    id = Column(Integer, primary_key=True)
    group = Column(Integer, ForeignKey("auth_group.id"), nullable=False)
    permission = Column(Integer, ForeignKey("auth_permission.id"), nullable=False)
