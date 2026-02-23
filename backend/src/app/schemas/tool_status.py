from typing import Optional

from pydantic import BaseModel, ConfigDict


class ToolStatusBase(BaseModel):
    name: str


class ToolStatusCreate(ToolStatusBase):
    pass


class ToolStatusUpdate(BaseModel):
    name: Optional[str] = None


class ToolStatusRead(ToolStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
