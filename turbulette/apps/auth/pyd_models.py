from typing import Optional
from datetime import datetime as dt
from pydantic import BaseModel, EmailStr, root_validator, ValidationError


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class AccessToken(BaseModel):
    access_token: Optional[str] = None


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
        pw1, pw2 = values.al
