from typing import Optional

from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    passwordhash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped["Department"] = relationship(back_populates="users", foreign_keys=[department_id])

    # Requests
    requested_loan_requests: Mapped[list["LoanRequest"]] = relationship(
        back_populates="requester",
        foreign_keys="LoanRequest.requester_user_id",
    )
    approved_loan_requests: Mapped[list["LoanRequest"]] = relationship(
        back_populates="approver",
        foreign_keys="LoanRequest.approver_user_id",
    )

    # Loans
    borrowed_loans: Mapped[list["Loan"]] = relationship(
        back_populates="borrower",
        foreign_keys="Loan.borrower_user_id",
    )
    issued_loans: Mapped[list["Loan"]] = relationship(
        back_populates="issuer",
        foreign_keys="Loan.issued_by_user_id",
    )
    returned_processed_loans: Mapped[list["Loan"]] = relationship(
        back_populates="return_processor",
        foreign_keys="Loan.returned_by_user_id",
    )