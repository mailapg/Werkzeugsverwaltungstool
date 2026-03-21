# ============================================================
# models/loan.py – Datenbank-Modell für Ausleihen
#
# Ein Loan repräsentiert eine aktive oder abgeschlossene Ausleihe.
# Er wird entweder direkt erstellt (vom Admin/Manager) oder
# automatisch aus einem genehmigten LoanRequest generiert.
#
# Status: Aktiv = returned_at ist NULL
#         Abgeschlossen = returned_at ist gesetzt
#         Überfällig = returned_at ist NULL UND due_at liegt in der Vergangenheit
# ============================================================

from typing import Optional

from sqlalchemy import ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)

    issued_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Wann wurde ausgegeben?
    returned_at: Mapped[Optional["DateTime"]] = mapped_column(DateTime(timezone=True))  # NULL = noch nicht zurückgegeben
    due_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)  # Fälligkeitsdatum
    comment: Mapped[Optional[str]] = mapped_column(Text)  # Optionaler Kommentar

    # Drei verschiedene Benutzerrollen bei einer Ausleihe:
    borrower_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)     # Wer leiht aus?
    issued_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)    # Wer hat ausgestellt?
    returned_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))        # Wer hat zurückgenommen?

    # Optionale Verlinkung zum ursprünglichen Antrag
    created_from_request_id: Mapped[Optional[int]] = mapped_column(ForeignKey("loan_requests.id"))

    # Beziehungen – foreign_keys zwingend nötig, da alle drei auf User zeigen
    borrower: Mapped["User"] = relationship(back_populates="borrowed_loans", foreign_keys=[borrower_user_id])
    issuer: Mapped["User"] = relationship(back_populates="issued_loans", foreign_keys=[issued_by_user_id])
    return_processor: Mapped[Optional["User"]] = relationship(
        back_populates="returned_processed_loans",
        foreign_keys=[returned_by_user_id],
    )

    # Zurückverfolgung zum Antrag (falls vorhanden)
    created_from_request: Mapped[Optional["LoanRequest"]] = relationship(back_populates="loans")

    # Welche konkreten Werkzeugeinheiten wurden ausgeliehen?
    # cascade="all, delete-orphan": LoanItems werden gelöscht wenn Loan gelöscht wird
    items: Mapped[list["LoanItem"]] = relationship(
        back_populates="loan",
        cascade="all, delete-orphan",
    )