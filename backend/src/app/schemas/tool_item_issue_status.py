from typing import Optional

from pydantic import BaseModel, ConfigDict


class ToolItemIssueStatusBase(BaseModel):
    name: str


class ToolItemIssueStatusCreate(ToolItemIssueStatusBase):
    pass


class ToolItemIssueStatusUpdate(BaseModel):
    name: Optional[str] = None


class ToolItemIssueStatusRead(ToolItemIssueStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
