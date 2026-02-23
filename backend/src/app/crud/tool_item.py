from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_item import ToolItem
from src.app.schemas.tool_item import ToolItemCreate, ToolItemUpdate


def get_tool_item(db: Session, item_id: int) -> Optional[ToolItem]:
    return db.get(ToolItem, item_id)


def get_tool_items(db: Session) -> list[ToolItem]:
    return db.query(ToolItem).all()


def get_tool_items_by_tool(db: Session, tool_id: int) -> list[ToolItem]:
    return db.query(ToolItem).filter(ToolItem.tool_id == tool_id).all()


def create_tool_item(db: Session, data: ToolItemCreate) -> ToolItem:
    item = ToolItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_tool_item(db: Session, item: ToolItem, data: ToolItemUpdate) -> ToolItem:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_tool_item(db: Session, item: ToolItem) -> None:
    db.delete(item)
    db.commit()
