from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.models.user import User
from src.app.schemas.loan_request import LoanRequestCreate, LoanRequestUpdate, LoanRequestRead, DecideRequest
import src.app.crud.loan_request as crud

router = APIRouter(tags=["Loan Requests"])


@router.get("/getloanrequests", response_model=list[LoanRequestRead])
def list_loan_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ADMIN sees all requests; DEPARTMENT_MANAGER sees only their department's requests."""
    if current_user.role.name == "DEPARTMENT_MANAGER":
        return crud.get_loan_requests_by_department(db, current_user.department_id)
    return crud.get_loan_requests(db)


@router.get("/getloanrequest/{request_id}", response_model=LoanRequestRead,
            dependencies=[Depends(get_current_user)])
def get_loan_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    return request


@router.post("/createloanrequest", response_model=LoanRequestRead, status_code=201,
             dependencies=[Depends(get_current_user)])
def create_loan_request(data: LoanRequestCreate, db: Session = Depends(get_db)):
    """Any authenticated user may submit a loan request."""
    try:
        return crud.create_loan_request(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/updateloanrequest/{request_id}", response_model=LoanRequestRead,
              dependencies=[Depends(get_current_user)])
def update_loan_request(request_id: int, data: LoanRequestUpdate, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    return crud.update_loan_request(db, request, data)


@router.patch("/decideloanrequest/{request_id}", response_model=LoanRequestRead,
              dependencies=[Depends(require_role("ADMIN", "DEPARTMENT_MANAGER"))])
def decide_loan_request(request_id: int, data: DecideRequest, db: Session = Depends(get_db)):
    """ADMIN or DEPARTMENT_MANAGER may approve or reject a loan request.
    On approval a Loan is automatically created."""
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    try:
        return crud.decide_loan_request(
            db,
            request,
            approver_user_id=data.approver_user_id,
            status_id=data.status_id,
            decision_comment=data.decision_comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/deleteloanrequest/{request_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_loan_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_loan_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Loan request not found")
    crud.delete_loan_request(db, request)
