from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.app.schemas.tool import ToolRead
from src.app.schemas.tool_status import ToolStatusRead
from src.app.schemas.tool_condition import ToolConditionRead
from src.app.schemas.user import UserSlim


class ToolItemBase(BaseModel):
    inventory_no: str
    description: Optional[str] = None
    tool_id: int
    status_id: int
    condition_id: int


class ToolItemCreate(BaseModel):
    inventory_no: str
    description: Optional[str] = None
    tool_id: int
    status_id: Optional[int] = None  # auto-set to AVAILABLE if not provided
    condition_id: int


class ToolItemUpdate(BaseModel):
    inventory_no: Optional[str] = None
    description: Optional[str] = None
    tool_id: Optional[int] = None
    status_id: Optional[int] = None
    condition_id: Optional[int] = None


class ToolItemSlim(BaseModel):
    id: int
    inventory_no: str
    tool_id: int

    model_config = ConfigDict(from_attributes=True)


class ToolItemRead(ToolItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tool: ToolRead
    status: ToolStatusRead
    condition: ToolConditionRead

    model_config = ConfigDict(from_attributes=True)


class ToolItemHistoryEntry(BaseModel):
    loan_id: int
    borrower: UserSlim
    issued_at: datetime
    due_at: datetime
    returned_at: Optional[datetime] = None
    return_condition: Optional[ToolConditionRead] = None
    return_comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
