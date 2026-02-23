from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.app.schemas.tool_item import ToolItemSlim
from src.app.schemas.tool_condition import ToolConditionRead


class LoanItemBase(BaseModel):
    tool_item_id: int
    loan_id: int
    return_comment: Optional[str] = None
    return_condition_id: Optional[int] = None


class LoanItemCreate(BaseModel):
    tool_item_id: int


class LoanItemStandaloneCreate(BaseModel):
    loan_id: int
    tool_item_id: int


class LoanItemUpdate(BaseModel):
    return_comment: Optional[str] = None
    return_condition_id: Optional[int] = None


class LoanItemRead(LoanItemBase):
    id: int
    tool_item: ToolItemSlim
    return_condition: Optional[ToolConditionRead] = None

    model_config = ConfigDict(from_attributes=True)
