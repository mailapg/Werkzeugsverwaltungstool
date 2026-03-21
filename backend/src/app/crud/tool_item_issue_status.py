from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_item_issue_status import ToolItemIssueStatus
from src.app.schemas.tool_item_issue_status import ToolItemIssueStatusCreate, ToolItemIssueStatusUpdate


def get_tool_item_issue_status(db: Session, status_id: int) -> Optional[ToolItemIssueStatus]:
    return db.get(ToolItemIssueStatus, status_id)


def get_tool_item_issue_statuses(
    db: Session
) -> list[ToolItemIssueStatus]:
    return db.query(ToolItemIssueStatus).all()


def create_tool_item_issue_status(db: Session, data: ToolItemIssueStatusCreate) -> ToolItemIssueStatus:
    status = ToolItemIssueStatus(**data.model_dump())
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def update_tool_item_issue_status(
    db: Session, status: ToolItemIssueStatus, data: ToolItemIssueStatusUpdate
) -> ToolItemIssueStatus:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(status, field, value)
    db.commit()
    db.refresh(status)
    return status


def delete_tool_item_issue_status(db: Session, status: ToolItemIssueStatus) -> None:
    db.delete(status)
    db.commit()
