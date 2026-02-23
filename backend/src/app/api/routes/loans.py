from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.loan import LoanCreate, LoanUpdate, LoanRead, ReturnLoanRequest
import src.app.crud.loan as crud

router = APIRouter(tags=["Loans"])


@router.get("/getloans", response_model=list[LoanRead])
def list_loans(db: Session = Depends(get_db)):
    return crud.get_loans(db)


@router.get("/getloan/{loan_id}", response_model=LoanRead)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.post("/createloan", response_model=LoanRead, status_code=201)
def create_loan(data: LoanCreate, db: Session = Depends(get_db)):
    return crud.create_loan(db, data)


@router.patch("/updateloan/{loan_id}", response_model=LoanRead)
def update_loan(loan_id: int, data: LoanUpdate, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return crud.update_loan(db, loan, data)


@router.patch("/returnloan/{loan_id}", response_model=LoanRead)
def return_loan(loan_id: int, data: ReturnLoanRequest, db: Session = Depends(get_db)):
    """Processes the return of a loan."""
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.returned_at is not None:
        raise HTTPException(status_code=409, detail="Loan has already been returned")
    item_returns = [i.model_dump() for i in data.items]
    return crud.return_loan(db, loan, data.returned_by_user_id, item_returns)


@router.delete("/deleteloan/{loan_id}", status_code=204)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    crud.delete_loan(db, loan)
