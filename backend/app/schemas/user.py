from pydantic import BaseModel, EmailStr, constr
import uuid
from enum import Enum

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserRead(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserRole(str, Enum):
    investigator = "investigator"
    admin = "admin"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.investigator  