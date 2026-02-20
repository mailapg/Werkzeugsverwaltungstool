from typing import Optional

from sqlalchemy import Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class LoanRequest(Base):
    __tablename__ = "loan_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    comment: Mapped[Optional[str]] = mapped_column(Text)

    requested_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)

    decision_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))
    decision_comment: Mapped[Optional[str]] = mapped_column(Text)

    requester_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approver_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    request_status_id: Mapped[int] = mapped_column(ForeignKey("loan_request_status.id"), nullable=False)

    requester: Mapped["User"] = relationship(
        back_populates="requested_loan_requests",
        foreign_keys=[requester_user_id],
    )
    approver: Mapped[Optional["User"]] = relationship(
        back_populates="approved_loan_requests",
        foreign_keys=[approver_user_id],
    )
    status: Mapped["LoanRequestStatus"] = relationship(back_populates="requests")

    items: Mapped[list["LoanRequestItem"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )

    loans: Mapped[list["Loan"]] = relationship(back_populates="created_from_request")