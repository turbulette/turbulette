from typing import Optional
from datetime import datetime as dt
from pydantic import BaseModel, EmailStr, root_validator


class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class BaseUserCreate(BaseModel):
    username: str
    email: EmailStr
    password_one: str
    password_two: str
    date_joined: dt = dt.utcnow()
    first_name: str
    last_name: str
    is_staff: bool = False


    @root_validator(pre=True)
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('password_one'), values.get('password_two')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return values
