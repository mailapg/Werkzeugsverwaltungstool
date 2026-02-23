from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.app.schemas.tool_category import ToolCategoryRead


class ToolBase(BaseModel):
    tool_name: str
    description: Optional[str] = None
    category_id: int


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    tool_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class ToolRead(ToolBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: ToolCategoryRead

    model_config = ConfigDict(from_attributes=True)
