from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class LoanItem(Base):
    __tablename__ = "loan_items"
    __table_args__ = (
        UniqueConstraint("loan_id", "tool_item_id", name="uq_loan_tool_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    return_comment: Mapped[Optional[str]] = mapped_column(Text)
    return_condition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tool_condition.id"))

    tool_item_id: Mapped[int] = mapped_column(ForeignKey("tool_items.id"), nullable=False)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False)

    loan: Mapped["Loan"] = relationship(back_populates="items")
    tool_item: Mapped["ToolItem"] = relationship(back_populates="loan_items")

    return_condition: Mapped[Optional["ToolCondition"]] = relationship(back_populates="loan_items")