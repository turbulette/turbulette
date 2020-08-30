from pydantic import BaseModel
from datetime import datetime


class CreateBook(BaseModel):
    title: str
    author: str
    publication_date: datetime
    profile: dict = None
