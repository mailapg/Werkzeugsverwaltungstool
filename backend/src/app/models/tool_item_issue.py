from typing import Optional

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ToolItemIssue(Base):
    __tablename__ = "tool_item_issues"

    id: Mapped[int] = mapped_column(primary_key=True)

    tool_item_id: Mapped[int] = mapped_column(ForeignKey("tool_items.id"), nullable=False)
    reported_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reported_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    status_id: Mapped[int] = mapped_column(ForeignKey("tool_item_issue_status.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    related_loan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("loans.id"))
    resolved_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))

    tool_item: Mapped["ToolItem"] = relationship(back_populates="issues")
    reported_by: Mapped["User"] = relationship(foreign_keys=[reported_by_user_id])
    status: Mapped["ToolItemIssueStatus"] = relationship(back_populates="issues")
    related_loan: Mapped[Optional["Loan"]] = relationship(foreign_keys=[related_loan_id])