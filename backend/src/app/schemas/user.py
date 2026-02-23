from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.app.schemas.role import RoleRead
from src.app.schemas.department import DepartmentRead


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    is_active: bool = True
    role_id: int
    department_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None
    department_id: Optional[int] = None
    password: Optional[str] = None


class UserSlim(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    role: RoleRead
    department: DepartmentRead

    model_config = ConfigDict(from_attributes=True)
