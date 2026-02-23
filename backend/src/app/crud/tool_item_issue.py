from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.tool_item_issue import ToolItemIssue
from src.app.schemas.tool_item_issue import ToolItemIssueCreate, ToolItemIssueUpdate


def get_tool_item_issue(db: Session, issue_id: int) -> Optional[ToolItemIssue]:
    return db.get(ToolItemIssue, issue_id)


def get_tool_item_issues(db: Session) -> list[ToolItemIssue]:
    return db.query(ToolItemIssue).all()


def get_issues_by_tool_item(db: Session, tool_item_id: int) -> list[ToolItemIssue]:
    return db.query(ToolItemIssue).filter(ToolItemIssue.tool_item_id == tool_item_id).all()


def create_tool_item_issue(db: Session, data: ToolItemIssueCreate) -> ToolItemIssue:
    issue = ToolItemIssue(**data.model_dump())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def update_tool_item_issue(
    db: Session, issue: ToolItemIssue, data: ToolItemIssueUpdate
) -> ToolItemIssue:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)
    db.commit()
    db.refresh(issue)
    return issue


def resolve_tool_item_issue(db: Session, issue: ToolItemIssue) -> ToolItemIssue:
    issue.resolved_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(issue)
    return issue


def delete_tool_item_issue(db: Session, issue: ToolItemIssue) -> None:
    db.delete(issue)
    db.commit()
