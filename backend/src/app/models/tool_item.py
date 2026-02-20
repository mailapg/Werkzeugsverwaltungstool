from typing import Optional

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ToolItem(Base):
    __tablename__ = "tool_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_no: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("tool_status.id"), nullable=False)
    condition_id: Mapped[int] = mapped_column(ForeignKey("tool_condition.id"), nullable=False)

    tool: Mapped["Tool"] = relationship(back_populates="items")
    status: Mapped["ToolStatus"] = relationship(back_populates="tool_items")
    condition: Mapped["ToolCondition"] = relationship(back_populates="tool_items")

    loan_items: Mapped[list["LoanItem"]] = relationship(back_populates="tool_item")

    issues: Mapped[list["ToolItemIssue"]] = relationship(back_populates="tool_item", cascade="all, delete-orphan")