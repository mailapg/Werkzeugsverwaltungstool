from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.loan_request import LoanRequest
from src.app.models.loan_request_item import LoanRequestItem
from src.app.schemas.loan_request import LoanRequestCreate, LoanRequestUpdate


def get_loan_request(db: Session, request_id: int) -> Optional[LoanRequest]:
    return db.get(LoanRequest, request_id)


def get_loan_requests(db: Session) -> list[LoanRequest]:
    return db.query(LoanRequest).all()


def get_loan_requests_by_user(db: Session, user_id: int) -> list[LoanRequest]:
    return db.query(LoanRequest).filter(LoanRequest.requester_user_id == user_id).all()


def create_loan_request(db: Session, data: LoanRequestCreate) -> LoanRequest:
    items_data = data.items
    request = LoanRequest(
        comment=data.comment,
        due_at=data.due_at,
        requester_user_id=data.requester_user_id,
        # Default status must be pre-seeded; caller should pass request_status_id
        # Here we rely on the first status entry (REQUESTED). A cleaner approach
        # would pass request_status_id in the schema, but we keep it simple.
        request_status_id=1,
    )
    db.add(request)
    db.flush()  # get request.id without committing

    for item_data in items_data:
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
    db.commit()
    db.refresh(request)
    return request


def delete_loan_request(db: Session, request: LoanRequest) -> None:
    db.delete(request)
    db.commit()
