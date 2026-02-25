from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.schemas.tool import ToolCreate, ToolUpdate, ToolRead
import src.app.crud.tool as crud

router = APIRouter(tags=["Tools"])


@router.get("/gettools", response_model=list[ToolRead],
            dependencies=[Depends(get_current_user)])
def list_tools(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    category_id: Optional[int] = None,
):
    return crud.get_tools(db, name=name, category_id=category_id)


@router.get("/gettool/{tool_id}", response_model=ToolRead,
            dependencies=[Depends(get_current_user)])
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.post("/createtool", response_model=ToolRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool(data: ToolCreate, db: Session = Depends(get_db)):
    return crud.create_tool(db, data)


@router.patch("/updatetool/{tool_id}", response_model=ToolRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool(tool_id: int, data: ToolUpdate, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return crud.update_tool(db, tool, data)


@router.delete("/deletetool/{tool_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = crud.get_tool(db, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    crud.delete_tool(db, tool)
