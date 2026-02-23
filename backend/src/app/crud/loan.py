from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.loan import Loan
from src.app.models.loan_item import LoanItem
from src.app.models.tool_item import ToolItem
from src.app.schemas.loan import LoanCreate, LoanUpdate

# ToolStatus name constants – must match seeded values
STATUS_LOANED = "LOANED"
STATUS_AVAILABLE = "AVAILABLE"
STATUS_DEFECT = "DEFECT"

# ToolCondition name constants – must match seeded values
CONDITION_DEFECT = "DEFECT"


def _get_status_id_by_name(db: Session, name: str) -> Optional[int]:
    from src.app.models.tool_status import ToolStatus
    status = db.query(ToolStatus).filter(ToolStatus.name == name).first()
    return status.id if status else None


def get_loan(db: Session, loan_id: int) -> Optional[Loan]:
    return db.get(Loan, loan_id)


def get_loans(db: Session) -> list[Loan]:
    return db.query(Loan).all()


def get_loans_by_borrower(db: Session, user_id: int) -> list[Loan]:
    return db.query(Loan).filter(Loan.borrower_user_id == user_id).all()


def create_loan(db: Session, data: LoanCreate) -> Loan:
    loaned_status_id = _get_status_id_by_name(db, STATUS_LOANED)

    loan = Loan(
        due_at=data.due_at,
        borrower_user_id=data.borrower_user_id,
        issued_by_user_id=data.issued_by_user_id,
        created_from_request_id=data.created_from_request_id,
    )
    db.add(loan)
    db.flush()

    for item_data in data.items:
        loan_item = LoanItem(
            loan_id=loan.id,
            tool_item_id=item_data.tool_item_id,
        )
        db.add(loan_item)

        # Mark tool item as LOANED
        if loaned_status_id:
            tool_item = db.get(ToolItem, item_data.tool_item_id)
            if tool_item:
                tool_item.status_id = loaned_status_id

    db.commit()
    db.refresh(loan)
    return loan


def update_loan(db: Session, loan: Loan, data: LoanUpdate) -> Loan:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(
    db: Session,
    loan: Loan,
    returned_by_user_id: int,
    item_returns: list[dict],
) -> Loan:
    """
    Process loan return.
    item_returns: list of {"loan_item_id": int, "return_comment": str|None, "return_condition_id": int|None}
    Sets returned_at, updates each LoanItem's return info, and restores ToolItem status.
    """
    available_status_id = _get_status_id_by_name(db, STATUS_AVAILABLE)
    defect_status_id = _get_status_id_by_name(db, STATUS_DEFECT)

    loan.returned_at = datetime.now(tz=timezone.utc)
    loan.returned_by_user_id = returned_by_user_id

    for ret in item_returns:
        loan_item = db.get(LoanItem, ret["loan_item_id"])
        if not loan_item or loan_item.loan_id != loan.id:
            continue
        loan_item.return_comment = ret.get("return_comment")
        loan_item.return_condition_id = ret.get("return_condition_id")

        # Restore ToolItem status based on return condition
        tool_item = db.get(ToolItem, loan_item.tool_item_id)
        if tool_item:
            from src.app.models.tool_condition import ToolCondition
            condition = db.get(ToolCondition, loan_item.return_condition_id) if loan_item.return_condition_id else None
            if condition and condition.name == CONDITION_DEFECT:
                tool_item.status_id = defect_status_id
            else:
                tool_item.status_id = available_status_id

    db.commit()
    db.refresh(loan)
    return loan


def delete_loan(db: Session, loan: Loan) -> None:
    db.delete(loan)
    db.commit()
