from turbulette.apps.auth.models import AbstractUser
from turbulette.db import Model

from sqlalchemy import Column, Integer, String

class BaseUser(Model, AbstractUser):
    pass

class CustomUser(Model, AbstractUser):
    USERNAME_FIELD = "id"
