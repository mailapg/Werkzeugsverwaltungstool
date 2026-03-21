import re
from typing import Annotated, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, AfterValidator

from src.app.schemas.role import RoleRead
from src.app.schemas.department import DepartmentRead

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(v: str) -> str:
    if not _EMAIL_RE.match(v):
        raise ValueError("Ungültige E-Mail-Adresse (erwartet: name@domain.tld)")
    return v


_EmailField = Annotated[str, AfterValidator(_validate_email)]


class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: str
    is_active: bool = True
    role_id: int
    department_id: int


class UserCreate(UserBase):
    email: _EmailField
    password: str


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[_EmailField] = None
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
