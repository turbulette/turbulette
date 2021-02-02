from typing import Optional
from datetime import datetime as dt
from pydantic import BaseModel, EmailStr, root_validator
from .core import get_password_hash


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None


class AccessToken(BaseModel):
    access_token: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None


class BaseUserCreate(BaseModel):
    """Base User model.

    The `hashed_password` shouldn't be supplied
    has it's filled by the root validator if passwords matches
    """

    username: str
    email: EmailStr
    password_one: str
    password_two: str
    hashed_password: Optional[str] = None
    date_joined: dt = dt.utcnow()
    first_name: str
    last_name: str
    is_staff: bool = False

    def dict(self, **kwargs):
        """Exclude clear passwords when exporting."""
        return super().dict(exclude={"password_one", "password_two"}, **kwargs)

    @root_validator(pre=True)
    def check_passwords_and_hash(cls, values):
        """Hash the password if it's confirmed."""
        pw1, pw2 = values.get("password_one"), values.get("password_two")
        if pw1 and pw2 and pw1 != pw2:
            raise ValueError("Passwords do not match")
        values["hashed_password"] = get_password_hash(pw1)
        return values
