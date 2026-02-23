from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.loan_item import LoanItemRead, LoanItemUpdate, LoanItemStandaloneCreate
import src.app.crud.loan_item as crud

router = APIRouter(tags=["Loan Items"])

@router.get("/getloanitems", response_model=list[LoanItemRead])
def list_loan_items(db: Session = Depends(get_db)):
    return crud.get_loan_items(db)


@router.get("/getloanitem/{item_id}", response_model=LoanItemRead)
def get_loan_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_loan_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan item not found")
    return item


@router.post("/createloanitem", response_model=LoanItemRead, status_code=201)
def create_loan_item(data: LoanItemStandaloneCreate, db: Session = Depends(get_db)):
    return crud.create_loan_item(db, data.loan_id, data.tool_item_id)


@router.patch("/updateloanitem/{item_id}", response_model=LoanItemRead)
def update_loan_item(item_id: int, data: LoanItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_loan_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan item not found")
    return crud.update_loan_item(db, item, data)


@router.delete("/deleteloanitem/{item_id}", status_code=204)
def delete_loan_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_loan_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Loan item not found")
    crud.delete_loan_item(db, item)
