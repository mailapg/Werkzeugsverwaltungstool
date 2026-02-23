from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoanRequestStatusBase(BaseModel):
    name: str


class LoanRequestStatusCreate(LoanRequestStatusBase):
    pass


class LoanRequestStatusUpdate(BaseModel):
    name: Optional[str] = None


class LoanRequestStatusRead(LoanRequestStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
