from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.app.schemas.tool import ToolRead


class LoanRequestItemBase(BaseModel):
    quantity: int = 1
    tool_id: int
    request_id: int


class LoanRequestItemCreate(BaseModel):
    quantity: int = 1
    tool_id: int


class LoanRequestItemStandaloneCreate(BaseModel):
    request_id: int
    tool_id: int
    quantity: int = 1


class LoanRequestItemUpdate(BaseModel):
    quantity: Optional[int] = None


class LoanRequestItemRead(LoanRequestItemBase):
    id: int
    tool: ToolRead

    model_config = ConfigDict(from_attributes=True)
