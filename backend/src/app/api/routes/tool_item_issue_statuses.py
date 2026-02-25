from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import require_role
from src.app.db.deps import get_db
from src.app.schemas.tool_item_issue_status import (
    ToolItemIssueStatusCreate,
    ToolItemIssueStatusUpdate,
    ToolItemIssueStatusRead,
)
import src.app.crud.tool_item_issue_status as crud

router = APIRouter(tags=["Tool Item Issue Statuses"])


@router.get("/gettoolitemissuestatuses", response_model=list[ToolItemIssueStatusRead],
            dependencies=[Depends(require_role("ADMIN"))])
def list_tool_item_issue_statuses(db: Session = Depends(get_db)):
    return crud.get_tool_item_issue_statuses(db)


@router.get("/gettoolitemissuestatus/{status_id}", response_model=ToolItemIssueStatusRead,
            dependencies=[Depends(require_role("ADMIN"))])
def get_tool_item_issue_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_tool_item_issue_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool item issue status not found")
    return status


@router.post("/createtoolitemissuestatus", response_model=ToolItemIssueStatusRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_tool_item_issue_status(data: ToolItemIssueStatusCreate, db: Session = Depends(get_db)):
    return crud.create_tool_item_issue_status(db, data)


@router.patch("/updatetoolitemissuestatus/{status_id}", response_model=ToolItemIssueStatusRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_tool_item_issue_status(
    status_id: int, data: ToolItemIssueStatusUpdate, db: Session = Depends(get_db)
):
    status = crud.get_tool_item_issue_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool item issue status not found")
    return crud.update_tool_item_issue_status(db, status, data)


@router.delete("/deletetoolitemissuestatus/{status_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_item_issue_status(status_id: int, db: Session = Depends(get_db)):
    status = crud.get_tool_item_issue_status(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tool item issue status not found")
    crud.delete_tool_item_issue_status(db, status)
