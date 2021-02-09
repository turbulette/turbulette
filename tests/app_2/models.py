from sqlalchemy import Column, String

from turbulette.apps.auth.models import AbstractUser
from turbulette.db import Model


class BaseUser(Model, AbstractUser):
    sex = Column(String)
