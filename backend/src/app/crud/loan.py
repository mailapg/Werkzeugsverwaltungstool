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


def get_loans(
    db: Session,
    borrower_user_id: Optional[int] = None,
    active_only: bool = False,
) -> list[Loan]:
    q = db.query(Loan)
    if borrower_user_id is not None:
        q = q.filter(Loan.borrower_user_id == borrower_user_id)
    if active_only:
        q = q.filter(Loan.returned_at.is_(None))
    return q.all()


def get_loans_by_borrower(db: Session, user_id: int) -> list[Loan]:
    return db.query(Loan).filter(Loan.borrower_user_id == user_id).all()


def get_overdue_loans(db: Session, department_id: Optional[int] = None) -> list[Loan]:
    """Returns all active loans past their due date."""
    now = datetime.now(tz=timezone.utc)
    q = (
        db.query(Loan)
        .filter(Loan.returned_at.is_(None), Loan.due_at < now)
    )
    if department_id is not None:
        from src.app.models.user import User
        q = q.join(User, Loan.borrower_user_id == User.id).filter(User.department_id == department_id)
    return q.all()


def _check_tool_item_availability(db: Session, tool_item_id: int) -> None:
    """Raises ValueError if the tool item is not AVAILABLE."""
    available_id = _get_status_id_by_name(db, STATUS_AVAILABLE)
    item = db.get(ToolItem, tool_item_id)
    if not item or item.status_id != available_id:
        raise ValueError(f"Tool item {tool_item_id} is not available for loan.")


def create_loan(db: Session, data: LoanCreate) -> Loan:
    for item_data in data.items:
        _check_tool_item_availability(db, item_data.tool_item_id)

    loaned_status_id = _get_status_id_by_name(db, STATUS_LOANED)

    loan = Loan(
        due_at=data.due_at,
        borrower_user_id=data.borrower_user_id,
        issued_by_user_id=data.issued_by_user_id,
        created_from_request_id=data.created_from_request_id,
        comment=data.comment,
    )
    db.add(loan)
    db.flush()

    for item_data in data.items:
        loan_item = LoanItem(
            loan_id=loan.id,
            tool_item_id=item_data.tool_item_id,
        )
        db.add(loan_item)

        if loaned_status_id:
            tool_item = db.get(ToolItem, item_data.tool_item_id)
            if tool_item:
                tool_item.status_id = loaned_status_id

    db.commit()
    db.refresh(loan)
    return loan


def create_loan_from_request(db: Session, request, approver_user_id: int) -> Loan:
    """
    Auto-creates a Loan when a LoanRequest is approved.
    Picks the first AVAILABLE ToolItem for each requested Tool.
    Raises ValueError if not enough available items exist.
    """
    available_id = _get_status_id_by_name(db, STATUS_AVAILABLE)
    loaned_id = _get_status_id_by_name(db, STATUS_LOANED)

    loan = Loan(
        due_at=request.due_at,
        borrower_user_id=request.requester_user_id,
        issued_by_user_id=approver_user_id,
        created_from_request_id=request.id,
        comment=request.comment,
    )
    db.add(loan)
    db.flush()

    for req_item in request.items:
        available_items = (
            db.query(ToolItem)
            .filter(ToolItem.tool_id == req_item.tool_id, ToolItem.status_id == available_id)
            .limit(req_item.quantity)
            .all()
        )
        if len(available_items) < req_item.quantity:
            raise ValueError(
                f"Cannot approve: not enough available items for tool {req_item.tool_id}."
            )
        for tool_item in available_items:
            db.add(LoanItem(loan_id=loan.id, tool_item_id=tool_item.id))
            tool_item.status_id = loaned_id

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

        tool_item = db.get(ToolItem, loan_item.tool_item_id)
        if tool_item:
            from src.app.models.tool_condition import ToolCondition
            condition = (
                db.get(ToolCondition, loan_item.return_condition_id)
                if loan_item.return_condition_id
                else None
            )
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
