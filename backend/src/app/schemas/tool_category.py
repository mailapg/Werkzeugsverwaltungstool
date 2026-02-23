from typing import Optional

from pydantic import BaseModel, ConfigDict


class ToolCategoryBase(BaseModel):
    name: str


class ToolCategoryCreate(ToolCategoryBase):
    pass


class ToolCategoryUpdate(BaseModel):
    name: Optional[str] = None


class ToolCategoryRead(ToolCategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
