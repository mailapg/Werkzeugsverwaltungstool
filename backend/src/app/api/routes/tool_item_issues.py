from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.tool_item_issue import ToolItemIssueCreate, ToolItemIssueUpdate, ToolItemIssueRead
import src.app.crud.tool_item_issue as crud

router = APIRouter(tags=["Tool Item Issues"])


@router.get("/gettoolitemissues", response_model=list[ToolItemIssueRead])
def list_tool_item_issues(db: Session = Depends(get_db)):
    return crud.get_tool_item_issues(db)


@router.get("/gettoolitemissue/{issue_id}", response_model=ToolItemIssueRead)
def get_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return issue


@router.post("/createtoolitemissue", response_model=ToolItemIssueRead, status_code=201)
def create_tool_item_issue(data: ToolItemIssueCreate, db: Session = Depends(get_db)):
    return crud.create_tool_item_issue(db, data)


@router.patch("/updatetoolitemissue/{issue_id}", response_model=ToolItemIssueRead)
def update_tool_item_issue(issue_id: int, data: ToolItemIssueUpdate, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return crud.update_tool_item_issue(db, issue, data)


@router.patch("/resolvetoolitemissue/{issue_id}", response_model=ToolItemIssueRead)
def resolve_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    """Marks a tool item issue as resolved."""
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    return crud.resolve_tool_item_issue(db, issue)


@router.delete("/deletetoolitemissue/{issue_id}", status_code=204)
def delete_tool_item_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = crud.get_tool_item_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Tool item issue not found")
    crud.delete_tool_item_issue(db, issue)
