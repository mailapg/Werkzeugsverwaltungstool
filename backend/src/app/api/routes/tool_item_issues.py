from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.schemas.tool_item_issue import ToolItemIssueCreate, ToolItemIssueUpdate, ToolItemIssueRead
import src.app.crud.tool_item_issue as crud

router = APIRouter(tags=["Tool Item Issues"])


@router.get("/gettoolitemissues", response_model=list[ToolItemIssueRead],
            dependencies=[Depends(get_current_user)])
def list_tool_item_issues(db: Session = Depends(get_db)):
    return crud.get_tool_item_issues(db)


@router.get("/gettoolitemissue/{issue_id}", response_model=ToolItemIssueRead,
            dependencies=[Depends(get_current_user)])
def get_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return issue


@router.post("/createtoolitemissue", response_model=ToolItemIssueRead, status_code=201,
             dependencies=[Depends(get_current_user)])
def create_tool_item_issue(data: ToolItemIssueCreate, db: Session = Depends(get_db)):
    """Any authenticated user may report an issue."""
    return crud.create_tool_item_issue(db, data)


@router.patch("/updatetoolitemissue/{issue_id}", response_model=ToolItemIssueRead,
              dependencies=[Depends(require_role("ADMIN", "DEPARTMENT_MANAGER"))])
def update_tool_item_issue(issue_id: int, data: ToolItemIssueUpdate, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return crud.update_tool_item_issue(db, issue, data)


@router.patch("/resolvetoolitemissue/{issue_id}", response_model=ToolItemIssueRead,
              dependencies=[Depends(require_role("ADMIN", "DEPARTMENT_MANAGER"))])
def resolve_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    """ADMIN or DEPARTMENT_MANAGER may resolve an issue."""
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return crud.resolve_tool_item_issue(db, issue)


@router.delete("/deletetoolitemissue/{issue_id}", status_code=204,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    crud.delete_tool_item_issue(db, issue)
