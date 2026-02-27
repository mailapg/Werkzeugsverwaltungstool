from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.schemas.tool_condition import ToolConditionCreate, ToolConditionUpdate, ToolConditionRead
import src.app.crud.tool_condition as crud

router = APIRouter(tags=["Tool Conditions"])


@router.get("/gettoolconditions", response_model=list[ToolConditionRead],
            dependencies=[Depends(get_current_user)])
def list_tool_conditions(db: Session = Depends(get_db)):
    return crud.get_tool_conditions(db)


@router.get("/gettoolcondition/{condition_id}", response_model=ToolConditionRead,
            dependencies=[Depends(get_current_user)])
def get_tool_condition(condition_id: int, db: Session = Depends(get_db)):
    condition = crud.get_tool_condition(db, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Tool condition not found")
    return condition


@router.post("/createtoolcondition", response_model=ToolConditionRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool_condition(data: ToolConditionCreate, db: Session = Depends(get_db)):
    return crud.create_tool_condition(db, data)


@router.patch("/updatetoolcondition/{condition_id}", response_model=ToolConditionRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool_condition(condition_id: int, data: ToolConditionUpdate, db: Session = Depends(get_db)):
    condition = crud.get_tool_condition(db, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Tool condition not found")
    return crud.update_tool_condition(db, condition, data)


@router.delete("/deletetoolcondition/{condition_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_condition(condition_id: int, db: Session = Depends(get_db)):
    condition = crud.get_tool_condition(db, condition_id)
    if not condition:
        raise HTTPException(status_code=404, detail="Tool condition not found")
    name = condition.name
    crud.delete_tool_condition(db, condition)
    return {"message": f"Werkzeugzustand '{name}' wurde gelöscht", "id": condition_id}
