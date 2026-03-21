from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class LoanRequestItem(Base):
    __tablename__ = "loan_request_items"
    __table_args__ = (
        UniqueConstraint("request_id", "tool_id", name="uq_request_tool"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")

    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"), nullable=False)
    request_id: Mapped[int] = mapped_column(ForeignKey("loan_requests.id"), nullable=False)

    tool: Mapped["Tool"] = relationship(back_populates="request_items")
    request: Mapped["LoanRequest"] = relationship(back_populates="items")