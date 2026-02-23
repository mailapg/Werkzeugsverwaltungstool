from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_condition import ToolCondition
from src.app.schemas.tool_condition import ToolConditionCreate, ToolConditionUpdate


def get_tool_condition(db: Session, condition_id: int) -> Optional[ToolCondition]:
    return db.get(ToolCondition, condition_id)


def get_tool_conditions(db: Session) -> list[ToolCondition]:
    return db.query(ToolCondition).all()


def create_tool_condition(db: Session, data: ToolConditionCreate) -> ToolCondition:
    condition = ToolCondition(**data.model_dump())
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition


def update_tool_condition(db: Session, condition: ToolCondition, data: ToolConditionUpdate) -> ToolCondition:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(condition, field, value)
    db.commit()
    db.refresh(condition)
    return condition


def delete_tool_condition(db: Session, condition: ToolCondition) -> None:
    db.delete(condition)
    db.commit()
