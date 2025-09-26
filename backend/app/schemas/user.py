from uuid import UUID
from pydantic import BaseModel, EmailStr
from enum import Enum

# Reuse the same roles you used in models
class UserRole(str, Enum):
    investigator = "investigator"
    admin = "admin"


# ---------- Base ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr


# ---------- Create ----------
class UserCreate(UserBase):
    password: str
    role: UserRole


# ---------- Read/Output ----------
class UserRead(UserBase):
    id: UUID
    role: UserRole

    class Config:
        orm_mode = True


# ---------- Response for APIs ----------
class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True
