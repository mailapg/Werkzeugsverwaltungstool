from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.tool_item import ToolItemCreate, ToolItemUpdate, ToolItemRead
import src.app.crud.tool_item as crud

router = APIRouter(tags=["Tool Items"])


@router.get("/gettoolitems", response_model=list[ToolItemRead])
def list_tool_items(db: Session = Depends(get_db)):
    return crud.get_tool_items(db)


@router.get("/gettoolitem/{item_id}", response_model=ToolItemRead)
def get_tool_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    return item


@router.post("/createtoolitem", response_model=ToolItemRead, status_code=201)
def create_tool_item(data: ToolItemCreate, db: Session = Depends(get_db)):
    return crud.create_tool_item(db, data)


@router.patch("/updatetoolitem/{item_id}", response_model=ToolItemRead)
def update_tool_item(item_id: int, data: ToolItemUpdate, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    return crud.update_tool_item(db, item, data)


@router.delete("/deletetoolitem/{item_id}", status_code=204)
def delete_tool_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_tool_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Tool item not found")
    crud.delete_tool_item(db, item)
