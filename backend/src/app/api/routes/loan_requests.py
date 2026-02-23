from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.loan_request import LoanRequestCreate, LoanRequestUpdate, LoanRequestRead, DecideRequest
import src.app.crud.loan_request as crud

router = APIRouter(tags=["Loan Requests"])


@router.get("/getloanrequests", response_model=list[LoanRequestRead])
def list_loan_requests(db: Session = Depends(get_db)):
    return crud.get_loan_requests(db)


@router.get("/getloanrequest/{request_id}", response_model=LoanRequestRead)
def get_loan_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    return request


@router.post("/createloanrequest", response_model=LoanRequestRead, status_code=201)
def create_loan_request(data: LoanRequestCreate, db: Session = Depends(get_db)):
    return crud.create_loan_request(db, data)


@router.patch("/updateloanrequest/{request_id}", response_model=LoanRequestRead)
def update_loan_request(request_id: int, data: LoanRequestUpdate, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    return crud.update_loan_request(db, request, data)


@router.patch("/decideloanrequest/{request_id}", response_model=LoanRequestRead)
def decide_loan_request(request_id: int, data: DecideRequest, db: Session = Depends(get_db)):
    """Approves or rejects a loan request."""
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    return crud.decide_loan_request(
        db,
        request,
        approver_user_id=data.approver_user_id,
        status_id=data.status_id,
        decision_comment=data.decision_comment,
    )


@router.delete("/deleteloanrequest/{request_id}", status_code=204)
def delete_loan_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    crud.delete_loan_request(db, request)
