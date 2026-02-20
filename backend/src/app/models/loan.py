from typing import Optional

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)

    issued_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    returned_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))
    due_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)

    borrower_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    issued_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    returned_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    created_from_request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("loan_requests.id"))

    borrower: Mapped["User"] = relationship(back_populates="borrowed_loans", foreign_keys=[borrower_user_id])
    issuer: Mapped["User"] = relationship(back_populates="issued_loans", foreign_keys=[issued_by_user_id])
    return_processor: Mapped[Optional["User"]] = relationship(
        back_populates="returned_processed_loans",
        foreign_keys=[returned_by_user_id],
    )

    created_from_request: Mapped[Optional["LoanRequest"]] = relationship(back_populates="loans")

    items: Mapped[list["LoanItem"]] = relationship(
        back_populates="loan",
        cascade="all, delete-orphan",
    )