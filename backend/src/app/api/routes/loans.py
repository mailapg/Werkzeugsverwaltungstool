from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.models.user import User
from src.app.schemas.loan import LoanCreate, LoanUpdate, LoanRead, ReturnLoanRequest
import src.app.crud.loan as crud

router = APIRouter(tags=["Loans"])


def _with_overdue_flag(loan) -> dict:
    data = LoanRead.model_validate(loan).model_dump()
    if loan.returned_at is None and loan.due_at < datetime.now(tz=timezone.utc):
        data["is_overdue"] = True
    return data


@router.get("/getloans", response_model=list[LoanRead],
            dependencies=[Depends(get_current_user)])
def list_loans(
    db: Session = Depends(get_db),
    borrower_user_id: Optional[int] = None,
    active_only: bool = False,
):
    return crud.get_loans(db, borrower_user_id=borrower_user_id, active_only=active_only)


@router.get("/getoverdueloans", response_model=list[LoanRead],
            dependencies=[Depends(require_role("ADMIN", "DEPARTMENT_MANAGER"))])
def list_overdue_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ADMIN sees all overdue loans; DEPARTMENT_MANAGER sees only their department."""
    dept_id = None
    if current_user.role.name == "DEPARTMENT_MANAGER":
        dept_id = current_user.department_id
    return crud.get_overdue_loans(db, department_id=dept_id)


@router.get("/getloan/{loan_id}", response_model=LoanRead,
            dependencies=[Depends(get_current_user)])
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.post("/createloan", response_model=LoanRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN", "DEPARTMENT_MANAGER"))])
def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
    """ADMIN or DEPARTMENT_MANAGER may issue a loan directly."""
    try:
        return crud.create_loan(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/updateloan/{loan_id}", response_model=LoanRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_loan(loan_id: int, data: LoanUpdate, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return crud.update_loan(db, loan, data)


@router.patch("/returnloan/{loan_id}", response_model=LoanRead,
              dependencies=[Depends(get_current_user)])
def return_loan(loan_id: int, data: ReturnLoanRequest, db: Session = Depends(get_db)):
    """Any authenticated user may return a loan (manual or via QR code scan)."""
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.returned_at is not None:
        raise HTTPException(status_code=409, detail="Loan has already been returned")
    item_returns = [i.model_dump() for i in data.items]
    return crud.return_loan(db, loan, data.returned_by_user_id, item_returns)


@router.delete("/deleteloan/{loan_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    crud.delete_loan(db, loan)
