from turbulette.apps.auth.models import AbstractUser
from turbulette.db import Model
from sqlalchemy import String, Column


class BaseUser(Model, AbstractUser):
    sex = Column(String)
