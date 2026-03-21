from typing import Optional

from pydantic import BaseModel, ConfigDict


class ToolConditionBase(BaseModel):
    name: str


class ToolConditionCreate(ToolConditionBase):
    pass


class ToolConditionUpdate(BaseModel):
    name: Optional[str] = None


class ToolConditionRead(ToolConditionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
