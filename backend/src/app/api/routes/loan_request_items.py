from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.loan_request_item import (
    LoanRequestItemRead,
    LoanRequestItemUpdate,
    LoanRequestItemStandaloneCreate,
)
import src.app.crud.loan_request_item as crud

router = APIRouter(tags=["Loan Request Items"])


@router.get("/getloanrequestitems", response_model=list[LoanRequestItemRead])
def list_loan_request_items(db: Session = Depends(get_db)):
    return crud.get_loan_request_items(db)


@router.get("/getloanrequestitem/{item_id}", response_model=LoanRequestItemRead)
def get_loan_request_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_loan_request_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan request item not found")
    return item


@router.post("/createloanrequestitem", response_model=LoanRequestItemRead, status_code=201)
def create_loan_request_item(data: LoanRequestItemStandaloneCreate, db: Session = Depends(get_db)):
    return crud.create_loan_request_item(db, data.request_id, data.tool_id, data.quantity)


@router.patch("/updateloanrequestitem/{item_id}", response_model=LoanRequestItemRead)
def update_loan_request_item(
    item_id: int, data: LoanRequestItemUpdate, db: Session = Depends(get_db)
):
    item = crud.get_loan_request_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan request item not found")
    return crud.update_loan_request_item(db, item, data)


@router.delete("/deleteloanrequestitem/{item_id}", status_code=204)
def delete_loan_request_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_loan_request_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan request item not found")
    crud.delete_loan_request_item(db, item)
