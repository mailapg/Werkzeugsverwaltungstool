from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import require_role
from src.app.db.deps import get_db
from src.app.schemas.loan_request_status import (
    LoanRequestStatusCreate,
    LoanRequestStatusUpdate,
    LoanRequestStatusRead,
)
import src.app.crud.loan_request_status as crud

router = APIRouter(tags=["Loan Request Statuses"])


@router.get("/getloanrequeststatuses", response_model=list[LoanRequestStatusRead],
            dependencies=[Depends(require_role("ADMIN"))])
def list_loan_request_statuses(db: Session = Depends(get_db)):
    return crud.get_loan_request_statuses(db)


@router.get("/getloanrequeststatus/{status_id}", response_model=LoanRequestStatusRead,
            dependencies=[Depends(require_role("ADMIN"))])
def get_loan_request_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_loan_request_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Loan request status not found")
    return status


@router.post("/createloanrequeststatus", response_model=LoanRequestStatusRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_loan_request_status(data: LoanRequestStatusCreate, db: Session = Depends(get_db)):
    return crud.create_loan_request_status(db, data)


@router.patch("/updateloanrequeststatus/{status_id}", response_model=LoanRequestStatusRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_loan_request_status(
    status_id: int, data: LoanRequestStatusUpdate, db: Session = Depends(get_db)
):
    status = crud.get_loan_request_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Loan request status not found")
    return crud.update_loan_request_status(db, status, data)


@router.delete("/deleteloanrequeststatus/{status_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_loan_request_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_loan_request_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Loan request status not found")
    crud.delete_loan_request_status(db, status)
