from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_item import ToolItem
from src.app.models.tool_status import ToolStatus
from src.app.schemas.tool_item import ToolItemCreate, ToolItemUpdate

_STATUS_AVAILABLE = "AVAILABLE"
_STATUS_RETIRED = "RETIRED"


def _get_status_id_by_name(db: Session, name: str) -> Optional[int]:
    status = db.query(ToolStatus).filter(ToolStatus.name == name).first()
    return status.id if status else None


def get_tool_item(db: Session, item_id: int) -> Optional[ToolItem]:
    return db.get(ToolItem, item_id)


def get_tool_items(
    db: Session,
    tool_id: Optional[int] = None,
    status_id: Optional[int] = None,
    condition_id: Optional[int] = None,
    inventory_no: Optional[str] = None,
) -> list[ToolItem]:
    q = db.query(ToolItem)
    if tool_id is not None:
        q = q.filter(ToolItem.tool_id == tool_id)
    if status_id is not None:
        q = q.filter(ToolItem.status_id == status_id)
    if condition_id is not None:
        q = q.filter(ToolItem.condition_id == condition_id)
    if inventory_no:
        q = q.filter(ToolItem.inventory_no.ilike(f"%{inventory_no}%"))
    return q.all()


def get_tool_items_by_tool(db: Session, tool_id: int) -> list[ToolItem]:
    return db.query(ToolItem).filter(ToolItem.tool_id == tool_id).all()


def create_tool_item(db: Session, data: ToolItemCreate) -> ToolItem:
    status_id = data.status_id
    if status_id is None:
        status_id = _get_status_id_by_name(db, _STATUS_AVAILABLE)

    item = ToolItem(
        inventory_no=data.inventory_no,
        description=data.description,
        tool_id=data.tool_id,
        status_id=status_id,
        condition_id=data.condition_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_tool_item(db: Session, item: ToolItem, data: ToolItemUpdate) -> ToolItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def retire_tool_item(db: Session, item: ToolItem) -> ToolItem:
    """Sets tool item status to RETIRED. Fails if item has an active (non-returned) loan."""
    from src.app.models.loan_item import LoanItem
    from src.app.models.loan import Loan

    active_loan = (
        db.query(Loan)
        .join(LoanItem, LoanItem.loan_id == Loan.id)
        .filter(LoanItem.tool_item_id == item.id, Loan.returned_at.is_(None))
        .first()
    )
    if active_loan:
        raise ValueError("Cannot retire a tool item with an active loan.")

    retired_id = _get_status_id_by_name(db, _STATUS_RETIRED)
    if not retired_id:
        raise ValueError("Status 'RETIRED' not found in database. Run the seed first.")

    item.status_id = retired_id
    db.commit()
    db.refresh(item)
    return item


def delete_tool_item(db: Session, item: ToolItem) -> None:
    db.delete(item)
    db.commit()


def get_tool_item_loan_history(db: Session, item_id: int) -> list[dict]:
    """Returns chronological loan history for a specific tool item."""
    from src.app.models.loan_item import LoanItem
    from src.app.models.loan import Loan
    from src.app.models.tool_condition import ToolCondition
    from src.app.models.user import User

    rows = (
        db.query(LoanItem, Loan)
        .join(Loan, LoanItem.loan_id == Loan.id)
        .filter(LoanItem.tool_item_id == item_id)
        .order_by(Loan.issued_at.asc())
        .all()
    )

    history = []
    for loan_item, loan in rows:
        condition = (
            db.get(ToolCondition, loan_item.return_condition_id)
            if loan_item.return_condition_id
            else None
        )
        borrower = db.get(User, loan.borrower_user_id)
        history.append({
            "loan_id": loan.id,
            "borrower": borrower,
            "issued_at": loan.issued_at,
            "due_at": loan.due_at,
            "returned_at": loan.returned_at,
            "return_condition": condition,
            "return_comment": loan_item.return_comment,
        })
    return history
