"""GINO models."""

from sqlalchemy import Column, String

from turbulette.apps.auth.models import AbstractUser
from gino_backend.model import Model


class BaseUser(Model, AbstractUser):
    sex = Column(String)
