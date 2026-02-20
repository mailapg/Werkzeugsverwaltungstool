from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ToolCategory(Base):
    __tablename__ = "tool_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    tools: Mapped[list["Tool"]] = relationship(back_populates="category")