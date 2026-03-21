from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.loan_request_status import LoanRequestStatus
from src.app.schemas.loan_request_status import LoanRequestStatusCreate, LoanRequestStatusUpdate


def get_loan_request_status(db: Session, status_id: int) -> Optional[LoanRequestStatus]:
    return db.get(LoanRequestStatus, status_id)


def get_loan_request_statuses(db: Session) -> list[LoanRequestStatus]:
    return db.query(LoanRequestStatus).all()


def create_loan_request_status(db: Session, data: LoanRequestStatusCreate) -> LoanRequestStatus:
    status = LoanRequestStatus(**data.model_dump())
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def update_loan_request_status(
    db: Session, status: LoanRequestStatus, data: LoanRequestStatusUpdate
) -> LoanRequestStatus:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(status, field, value)
    db.commit()
    db.refresh(status)
    return status


def delete_loan_request_status(db: Session, status: LoanRequestStatus) -> None:
    db.delete(status)
    db.commit()
