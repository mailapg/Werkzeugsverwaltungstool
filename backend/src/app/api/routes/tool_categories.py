from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.tool_category import ToolCategoryCreate, ToolCategoryUpdate, ToolCategoryRead
import src.app.crud.tool_category as crud

router = APIRouter(tags=["Tool Categories"])


@router.get("/gettoolcategories", response_model=list[ToolCategoryRead])
def list_tool_categories(db: Session = Depends(get_db)):
    return crud.get_tool_categories(db)


@router.get("/gettoolcategory/{category_id}", response_model=ToolCategoryRead)
def get_tool_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_tool_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Tool category not found")
    return category


@router.post("/createtoolcategory", response_model=ToolCategoryRead, status_code=201)
def create_tool_category(data: ToolCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_tool_category(db, data)


@router.patch("/updatetoolcategory/{category_id}", response_model=ToolCategoryRead)
def update_tool_category(category_id: int, data: ToolCategoryUpdate, db: Session = Depends(get_db)):
    category = crud.get_tool_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Tool category not found")
    return crud.update_tool_category(db, category, data)


@router.delete("/deletetoolcategory/{category_id}", status_code=204)
def delete_tool_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_tool_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Tool category not found")
    crud.delete_tool_category(db, category)
