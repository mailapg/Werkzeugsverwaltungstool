from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.app.schemas.tool_item import ToolItemSlim
from src.app.schemas.tool_item_issue_status import ToolItemIssueStatusRead
from src.app.schemas.user import UserSlim


class ToolItemIssueBase(BaseModel):
    tool_item_id: int
    reported_by_user_id: int
    status_id: int
    title: str
    description: Optional[str] = None
    related_loan_id: Optional[int] = None


class ToolItemIssueCreate(ToolItemIssueBase):
    pass


class ToolItemIssueUpdate(BaseModel):
    status_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    related_loan_id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class ToolItemIssueRead(ToolItemIssueBase):
    id: int
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    tool_item: ToolItemSlim
    reported_by: UserSlim
    status: ToolItemIssueStatusRead

    model_config = ConfigDict(from_attributes=True)
