from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.app.schemas.user import UserSlim
from src.app.schemas.loan_request_status import LoanRequestStatusRead
from src.app.schemas.loan_request_item import LoanRequestItemCreate, LoanRequestItemRead


class LoanRequestBase(BaseModel):
    comment: Optional[str] = None
    due_at: datetime
    requester_user_id: int


class LoanRequestCreate(LoanRequestBase):
    items: list[LoanRequestItemCreate]


class LoanRequestUpdate(BaseModel):
    comment: Optional[str] = None
    due_at: Optional[datetime] = None
    decision_comment: Optional[str] = None
    approver_user_id: Optional[int] = None
    request_status_id: Optional[int] = None


class DecideRequest(BaseModel):
    approver_user_id: int
    status_id: int
    decision_comment: Optional[str] = None


class LoanRequestRead(LoanRequestBase):
    id: int
    requested_at: datetime
    decision_at: Optional[datetime] = None
    decision_comment: Optional[str] = None
    approver_user_id: Optional[int] = None
    request_status_id: int
    requester: UserSlim
    approver: Optional[UserSlim] = None
    status: LoanRequestStatusRead
    items: list[LoanRequestItemRead]

    model_config = ConfigDict(from_attributes=True)
