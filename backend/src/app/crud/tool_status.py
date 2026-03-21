from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_status import ToolStatus
from src.app.schemas.tool_status import ToolStatusCreate, ToolStatusUpdate


def get_tool_status(db: Session, status_id: int) -> Optional[ToolStatus]:
    return db.get(ToolStatus, status_id)


def get_tool_statuses(db: Session) -> list[ToolStatus]:
    return db.query(ToolStatus).all()


def create_tool_status(db: Session, data: ToolStatusCreate) -> ToolStatus:
    status = ToolStatus(**data.model_dump())
    db.add(status)
    db.commit()
    db.refresh(status)
    return status


def update_tool_status(db: Session, status: ToolStatus, data: ToolStatusUpdate) -> ToolStatus:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(status, field, value)
    db.commit()
    db.refresh(status)
    return status


def delete_tool_status(db: Session, status: ToolStatus) -> None:
    db.delete(status)
    db.commit()
