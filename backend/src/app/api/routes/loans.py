from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.core.role_ids import ADMIN_ID, MANAGER_ID, EMPLOYEE_ID
from src.app.db.deps import get_db
from src.app.models.user import User
from src.app.schemas.loan import LoanCreate, LoanUpdate, LoanRead, ReturnLoanRequest
import src.app.crud.loan as crud

router = APIRouter(tags=["Loans"])


def _with_overdue_flag(loan) -> dict:
    data = LoanRead.model_validate(loan).model_dump()
    due = loan.due_at.replace(tzinfo=timezone.utc) if loan.due_at.tzinfo is None else loan.due_at
    if loan.returned_at is None and due < datetime.now(tz=timezone.utc):
        data["is_overdue"] = True
    return data


@router.get("/getloans", response_model=list[LoanRead])
def list_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    active_only: bool = False,
):
    """ADMIN sees all; DEPARTMENT_MANAGER sees their department; EMPLOYEE sees only their own."""
    if current_user.role_id == EMPLOYEE_ID:
        loans = crud.get_loans(db, borrower_user_id=current_user.id, active_only=active_only)
    elif current_user.role_id == MANAGER_ID:
        loans = crud.get_loans_by_department(db, current_user.department_id)
    else:
        loans = crud.get_loans(db, active_only=active_only)
    return [_with_overdue_flag(loan) for loan in loans]


@router.get("/getoverdueloans", response_model=list[LoanRead],
            dependencies=[Depends(require_role(ADMIN_ID, MANAGER_ID))])
def list_overdue_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """ADMIN sees all overdue loans; DEPARTMENT_MANAGER sees only their department."""
    dept_id = None
    if current_user.role_id == MANAGER_ID:
        dept_id = current_user.department_id
    return crud.get_overdue_loans(db, department_id=dept_id)


@router.get("/getloan/{loan_id}", response_model=LoanRead,
            dependencies=[Depends(get_current_user)])
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    return loan


@router.post("/createloan", response_model=LoanRead, status_code=201,
             dependencies=[Depends(require_role(ADMIN_ID, MANAGER_ID))])
def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
    """ADMIN or DEPARTMENT_MANAGER may issue a loan directly."""
    try:
        return crud.create_loan(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch("/updateloan/{loan_id}", response_model=LoanRead,
              dependencies=[Depends(require_role(ADMIN_ID))])
def update_loan(loan_id: int, data: LoanUpdate, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    return crud.update_loan(db, loan, data)


@router.patch("/returnloan/{loan_id}", response_model=LoanRead,
              dependencies=[Depends(get_current_user)])
def return_loan(loan_id: int, data: ReturnLoanRequest, db: Session = Depends(get_db)):
    """Any authenticated user may return a loan (manual or via QR code scan)."""
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    if loan.returned_at is not None:
        raise HTTPException(status_code=409, detail="Diese Ausleihe wurde bereits zurückgegeben")
    item_returns = [i.model_dump() for i in data.items]
    return crud.return_loan(db, loan, data.returned_by_user_id, item_returns)


@router.delete("/deleteloan/{loan_id}", status_code=200,
               dependencies=[Depends(require_role(ADMIN_ID))])
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    crud.delete_loan(db, loan)
    return {"message": f"Ausleihe #{loan_id} wurde gelöscht", "id": loan_id}
