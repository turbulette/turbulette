"""GINO models."""

from gino.json_support import ObjectProperty
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.sqltypes import Float, String

from turbulette.apps.auth.models import AbstractUser
from gino_backend.model import Model


class BaseUser(Model, AbstractUser):
    pass


class CustomUser(AbstractUser, Model):
    pass


class Book(Model):
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    publication_date = Column(DateTime(), nullable=False)
    book_profile = Column(JSONB, nullable=False, server_default="{}")
    profile = ObjectProperty(prop_name="book_profile")
    borrowings = Column(Integer, default=0)
    price_bought = Column(Float)


class Comics(Model):
    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey("app_1_book.id"), nullable=False)
    artist = Column(String)
