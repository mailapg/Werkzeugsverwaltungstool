from typing import Optional

from sqlalchemy.orm import Session

from src.app.models.loan_item import LoanItem
from src.app.schemas.loan_item import LoanItemUpdate


def get_loan_item(db: Session, item_id: int) -> Optional[LoanItem]:
    return db.get(LoanItem, item_id)


def get_loan_items(db: Session) -> list[LoanItem]:
    return db.query(LoanItem).all()


def create_loan_item(db: Session, loan_id: int, tool_item_id: int) -> LoanItem:
    item = LoanItem(loan_id=loan_id, tool_item_id=tool_item_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_loan_item(db: Session, item: LoanItem, data: LoanItemUpdate) -> LoanItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_loan_item(db: Session, item: LoanItem) -> None:
    db.delete(item)
    db.commit()
