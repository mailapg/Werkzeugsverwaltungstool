from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool_category import ToolCategory
from src.app.schemas.tool_category import ToolCategoryCreate, ToolCategoryUpdate


def get_tool_category(db: Session, category_id: int) -> Optional[ToolCategory]:
    return db.get(ToolCategory, category_id)


def get_tool_categories(db: Session) -> list[ToolCategory]:
    return db.query(ToolCategory).all()


def create_tool_category(db: Session, data: ToolCategoryCreate) -> ToolCategory:
    category = ToolCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_tool_category(db: Session, category: ToolCategory, data: ToolCategoryUpdate) -> ToolCategory:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_tool_category(db: Session, category: ToolCategory) -> None:
    db.delete(category)
    db.commit()
