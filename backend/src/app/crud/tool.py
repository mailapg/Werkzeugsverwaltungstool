from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.tool import Tool
from src.app.schemas.tool import ToolCreate, ToolUpdate


def get_tool(db: Session, tool_id: int) -> Optional[Tool]:
    return db.get(Tool, tool_id)


def get_tools(
    db: Session,
    name: Optional[str] = None,
    category_id: Optional[int] = None,
) -> list[Tool]:
    q = db.query(Tool)
    if name:
        q = q.filter(Tool.tool_name.ilike(f"%{name}%"))
    if category_id is not None:
        q = q.filter(Tool.category_id == category_id)
    return q.all()


def create_tool(db: Session, data: ToolCreate) -> Tool:
    tool = Tool(**data.model_dump())
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


def update_tool(db: Session, tool: Tool, data: ToolUpdate) -> Tool:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)
    db.commit()
    db.refresh(tool)
    return tool


def delete_tool(db: Session, tool: Tool) -> None:
    db.delete(tool)
    db.commit()


def set_tool_image(db: Session, tool: Tool, filename: Optional[str]) -> Tool:
    tool.image_filename = filename
    db.commit()
    db.refresh(tool)
    return tool
