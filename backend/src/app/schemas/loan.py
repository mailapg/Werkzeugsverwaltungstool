from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.app.schemas.user import UserSlim
from src.app.schemas.loan_item import LoanItemCreate, LoanItemRead


class LoanBase(BaseModel):
    due_at: datetime
    borrower_user_id: int
    issued_by_user_id: int
    created_from_request_id: Optional[int] = None


class LoanCreate(LoanBase):
    items: list[LoanItemCreate]


class LoanUpdate(BaseModel):
    returned_at: Optional[datetime] = None
    returned_by_user_id: Optional[int] = None


class LoanItemReturn(BaseModel):
    loan_item_id: int
    return_comment: Optional[str] = None
    return_condition_id: Optional[int] = None


class ReturnLoanRequest(BaseModel):
    returned_by_user_id: int
    items: list[LoanItemReturn]


class LoanRead(LoanBase):
    id: int
    issued_at: datetime
    returned_at: Optional[datetime] = None
    returned_by_user_id: Optional[int] = None
    borrower: UserSlim
    issuer: UserSlim
    return_processor: Optional[UserSlim] = None
    items: list[LoanItemRead]

    model_config = ConfigDict(from_attributes=True)
