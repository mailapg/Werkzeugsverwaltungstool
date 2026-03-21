from typing import Optional

from sqlalchemy.orm import Session

from src.app.models.loan_request_item import LoanRequestItem
from src.app.schemas.loan_request_item import LoanRequestItemUpdate


def get_loan_request_item(db: Session, item_id: int) -> Optional[LoanRequestItem]:
    return db.get(LoanRequestItem, item_id)


def get_loan_request_items(db: Session) -> list[LoanRequestItem]:
    return db.query(LoanRequestItem).all()


def create_loan_request_item(
    db: Session, request_id: int, tool_id: int, quantity: int = 1
) -> LoanRequestItem:
    item = LoanRequestItem(request_id=request_id, tool_id=tool_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_loan_request_item(
    db: Session, item: LoanRequestItem, data: LoanRequestItemUpdate
) -> LoanRequestItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_loan_request_item(db: Session, item: LoanRequestItem) -> None:
    db.delete(item)
    db.commit()
