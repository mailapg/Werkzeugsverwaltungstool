from typing import Optional

from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    lead_user_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    lead_user_id: Optional[int] = None


class DepartmentRead(DepartmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
