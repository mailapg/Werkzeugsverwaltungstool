from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.tool_item_issue import ToolItemIssue
from src.app.models.tool_item import ToolItem
from src.app.models.tool_status import ToolStatus
from src.app.models.tool_condition import ToolCondition
from src.app.models.tool_item_issue_status import ToolItemIssueStatus
from src.app.models.loan_item import LoanItem
from src.app.models.loan import Loan
from src.app.schemas.tool_item_issue import ToolItemIssueCreate, ToolItemIssueUpdate

_RESOLVED_STATUSES = {"RESOLVED", "CLOSED"}
_OPEN_STATUSES = {"OPEN", "IN_PROGRESS"}


def _get_tool_status_id(db: Session, name: str) -> Optional[int]:
    s = db.query(ToolStatus).filter(ToolStatus.name == name).first()
    return s.id if s else None


def _get_tool_condition_id(db: Session, name: str) -> Optional[int]:
    c = db.query(ToolCondition).filter(ToolCondition.name == name).first()
    return c.id if c else None


def _set_tool_item_status(db: Session, tool_item_id: int, status_name: str) -> None:
    status_id = _get_tool_status_id(db, status_name)
    if status_id is None:
        return
    tool_item = db.get(ToolItem, tool_item_id)
    if tool_item:
        tool_item.status_id = status_id


def _set_tool_item_condition(db: Session, tool_item_id: int, condition_name: str) -> None:
    condition_id = _get_tool_condition_id(db, condition_name)
    if condition_id is None:
        return
    tool_item = db.get(ToolItem, tool_item_id)
    if tool_item:
        tool_item.condition_id = condition_id


def _is_on_active_loan(db: Session, tool_item_id: int) -> bool:
    """Returns True if the tool item is currently on an unreturned loan."""
    return (
        db.query(LoanItem)
        .join(Loan, LoanItem.loan_id == Loan.id)
        .filter(LoanItem.tool_item_id == tool_item_id, Loan.returned_at.is_(None))
        .first()
    ) is not None


def _has_open_issues(db: Session, tool_item_id: int, exclude_issue_id: Optional[int] = None) -> bool:
    """Returns True if the tool item still has open (OPEN/IN_PROGRESS) issues."""
    open_status_ids = [
        s.id for s in db.query(ToolItemIssueStatus).all()
        if s.name in _OPEN_STATUSES
    ]
    query = db.query(ToolItemIssue).filter(
        ToolItemIssue.tool_item_id == tool_item_id,
        ToolItemIssue.status_id.in_(open_status_ids),
    )
    if exclude_issue_id is not None:
        query = query.filter(ToolItemIssue.id != exclude_issue_id)
    return query.first() is not None


def get_tool_item_issue(db: Session, issue_id: int) -> Optional[ToolItemIssue]:
    return db.get(ToolItemIssue, issue_id)


def get_tool_item_issues(db: Session) -> list[ToolItemIssue]:
    return db.query(ToolItemIssue).all()


def get_issues_by_tool_item(db: Session, tool_item_id: int) -> list[ToolItemIssue]:
    return db.query(ToolItemIssue).filter(ToolItemIssue.tool_item_id == tool_item_id).all()


def create_tool_item_issue(db: Session, data: ToolItemIssueCreate) -> ToolItemIssue:
    issue = ToolItemIssue(**data.model_dump())
    db.add(issue)
    _set_tool_item_status(db, data.tool_item_id, "MAINTENANCE")
    _set_tool_item_condition(db, data.tool_item_id, "WORN")
    db.commit()
    db.refresh(issue)
    return issue


def update_tool_item_issue(
    db: Session, issue: ToolItemIssue, data: ToolItemIssueUpdate
) -> ToolItemIssue:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    if data.status_id is not None:
        status = db.get(ToolItemIssueStatus, data.status_id)
        if status and status.name in _RESOLVED_STATUSES:
            if not _has_open_issues(db, issue.tool_item_id, exclude_issue_id=issue.id) \
                    and not _is_on_active_loan(db, issue.tool_item_id):
                _set_tool_item_status(db, issue.tool_item_id, "AVAILABLE")
                _set_tool_item_condition(db, issue.tool_item_id, "OK")
        elif status and status.name in _OPEN_STATUSES:
            _set_tool_item_status(db, issue.tool_item_id, "MAINTENANCE")
            _set_tool_item_condition(db, issue.tool_item_id, "WORN")

    db.commit()
    db.refresh(issue)
    return issue


def resolve_tool_item_issue(db: Session, issue: ToolItemIssue) -> ToolItemIssue:
    issue.resolved_at = datetime.now(tz=timezone.utc)
    if not _has_open_issues(db, issue.tool_item_id, exclude_issue_id=issue.id) \
            and not _is_on_active_loan(db, issue.tool_item_id):
        _set_tool_item_status(db, issue.tool_item_id, "AVAILABLE")
        _set_tool_item_condition(db, issue.tool_item_id, "OK")
    db.commit()
    db.refresh(issue)
    return issue


def delete_tool_item_issue(db: Session, issue: ToolItemIssue) -> None:
    current_status = db.get(ToolItemIssueStatus, issue.status_id)
    if current_status and current_status.name in _OPEN_STATUSES:
        if not _has_open_issues(db, issue.tool_item_id, exclude_issue_id=issue.id) \
                and not _is_on_active_loan(db, issue.tool_item_id):
            _set_tool_item_status(db, issue.tool_item_id, "AVAILABLE")
            _set_tool_item_condition(db, issue.tool_item_id, "OK")
    db.delete(issue)
    db.commit()
