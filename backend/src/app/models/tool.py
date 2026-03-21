from typing import Optional

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    tool_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_filename: Mapped[Optional[str]] = mapped_column(String(255))

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("tool_categories.id"), nullable=False)

    category: Mapped["ToolCategory"] = relationship(back_populates="tools")
    items: Mapped[list["ToolItem"]] = relationship(back_populates="tool")

    request_items: Mapped[list["LoanRequestItem"]] = relationship(back_populates="tool")