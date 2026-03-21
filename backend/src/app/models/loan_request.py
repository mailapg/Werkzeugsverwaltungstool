# ============================================================
# models/loan_request.py – Datenbank-Modell für Ausleiheanträge
#
# Ein LoanRequest ist ein Antrag eines Mitarbeiters auf Werkzeugausleihe.
# Workflow: REQUESTED → APPROVED/REJECTED/CANCELLED
# Bei Genehmigung wird automatisch ein Loan-Objekt erstellt.
# ============================================================

from typing import Optional

from sqlalchemy import Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class LoanRequest(Base):
    __tablename__ = "loan_requests"

    id: Mapped[int] = mapped_column(primary_key=True)

    comment: Mapped[Optional[str]] = mapped_column(Text)  # Kommentar des Antragstellers

    days_needed: Mapped[Optional[int]] = mapped_column(nullable=True)  # Wie viele Tage wird die Ausleihe benötigt?

    requested_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Wann wurde der Antrag gestellt?
    loan_start_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))  # Gewünschter Starttermin
    due_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True), nullable=True)  # Gewünschtes Rückgabedatum

    decision_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))  # Wann wurde entschieden?
    decision_comment: Mapped[Optional[str]] = mapped_column(Text)  # Kommentar des Genehmigers

    # Wer hat den Antrag gestellt?
    requester_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # Wer hat genehmigt/abgelehnt? (leer solange noch offen)
    approver_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Status des Antrags: REQUESTED / APPROVED / REJECTED / CANCELLED
    request_status_id: Mapped[int] = mapped_column(ForeignKey("loan_request_status.id"), nullable=False)

    # Beziehungen – foreign_keys nötig, da beide auf User zeigen
    requester: Mapped["User"] = relationship(
        back_populates="requested_loan_requests",
        foreign_keys=[requester_user_id],
    )
    approver: Mapped[Optional["User"]] = relationship(
        back_populates="approved_loan_requests",
        foreign_keys=[approver_user_id],
    )
    status: Mapped["LoanRequestStatus"] = relationship(back_populates="requests")

    # Welche Werkzeuge (und wie viele) wurden beantragt?
    # cascade="all, delete-orphan": Wenn der Antrag gelöscht wird, werden auch die Items gelöscht
    items: Mapped[list["LoanRequestItem"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
    )

    # Die aus diesem Antrag erstellten Ausleihen (nach Genehmigung)
    loans: Mapped[list["Loan"]] = relationship(back_populates="created_from_request")