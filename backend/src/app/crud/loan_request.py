from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.loan_request import LoanRequest
from src.app.models.loan_request_item import LoanRequestItem
from src.app.models.loan_request_status import LoanRequestStatus
from src.app.models.tool_item import ToolItem
from src.app.models.tool_status import ToolStatus
from src.app.schemas.loan_request import LoanRequestCreate, LoanRequestUpdate

_STATUS_REQUESTED = "REQUESTED"
_STATUS_APPROVED = "APPROVED"
_STATUS_AVAILABLE = "AVAILABLE"


def _get_requested_status_id(db: Session) -> int:
    status = db.query(LoanRequestStatus).filter(LoanRequestStatus.name == _STATUS_REQUESTED).first()
    if not status:
        raise ValueError(f"LoanRequestStatus '{_STATUS_REQUESTED}' not found. Run the seed first.")
    return status.id


def _get_tool_status_id(db: Session, name: str) -> Optional[int]:
    status = db.query(ToolStatus).filter(ToolStatus.name == name).first()
    return status.id if status else None


def _check_tool_availability(db: Session, tool_id: int, quantity: int) -> None:
    """Raises ValueError if not enough available tool items exist for the given tool."""
    available_id = _get_tool_status_id(db, _STATUS_AVAILABLE)
    count = (
        db.query(ToolItem)
        .filter(ToolItem.tool_id == tool_id, ToolItem.status_id == available_id)
        .count()
    )
    if count < quantity:
        raise ValueError(
            f"Not enough available items for tool {tool_id}: "
            f"requested {quantity}, available {count}."
        )


def get_loan_request(db: Session, request_id: int) -> Optional[LoanRequest]:
    return db.get(LoanRequest, request_id)


def get_loan_requests(db: Session) -> list[LoanRequest]:
    return db.query(LoanRequest).all()


def get_loan_requests_by_user(db: Session, user_id: int) -> list[LoanRequest]:
    return db.query(LoanRequest).filter(LoanRequest.requester_user_id == user_id).all()


def get_loan_requests_by_department(db: Session, department_id: int) -> list[LoanRequest]:
    """Returns all loan requests from users in the given department."""
    from src.app.models.user import User
    return (
        db.query(LoanRequest)
        .join(User, LoanRequest.requester_user_id == User.id)
        .filter(User.department_id == department_id)
        .all()
    )


def create_loan_request(db: Session, data: LoanRequestCreate) -> LoanRequest:
    for item_data in data.items:
        _check_tool_availability(db, item_data.tool_id, item_data.quantity)

    request = LoanRequest(
        comment=data.comment,
        loan_start_at=data.loan_start_at,
        due_at=data.due_at,
        requester_user_id=data.requester_user_id,
        request_status_id=_get_requested_status_id(db),
    )
    db.add(request)
    db.flush()

    for item_data in data.items:
        loan_request_item = LoanRequestItem(
            request_id=request.id,
            tool_id=item_data.tool_id,
            quantity=item_data.quantity,
        )
        db.add(loan_request_item)

    db.commit()
    db.refresh(request)
    return request


def update_loan_request(db: Session, request: LoanRequest, data: LoanRequestUpdate) -> LoanRequest:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(request, field, value)
    db.commit()
    db.refresh(request)
    return request


def decide_loan_request(
    db: Session,
    request: LoanRequest,
    approver_user_id: int,
    status_id: int,
    decision_comment: Optional[str] = None,
) -> LoanRequest:
    request.approver_user_id = approver_user_id
    request.request_status_id = status_id
    request.decision_comment = decision_comment
    request.decision_at = datetime.now(tz=timezone.utc)
    db.flush()

    # Auto-create a Loan when the request is approved
    status_obj = db.get(LoanRequestStatus, status_id)
    if status_obj and status_obj.name == _STATUS_APPROVED:
        from src.app.crud.loan import create_loan_from_request
        create_loan_from_request(db, request, approver_user_id)

    db.commit()
    db.refresh(request)
    return request


def delete_loan_request(db: Session, request: LoanRequest) -> None:
    db.delete(request)
    db.commit()
