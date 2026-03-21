from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class LoanRequestStatus(Base):
    __tablename__ = "loan_request_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    requests: Mapped[list["LoanRequest"]] = relationship(back_populates="status")