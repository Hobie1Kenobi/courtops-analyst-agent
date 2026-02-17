from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UserBase(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str
    role: UserRole


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str

