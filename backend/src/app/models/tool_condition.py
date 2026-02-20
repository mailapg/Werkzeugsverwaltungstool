from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ToolCondition(Base):
    __tablename__ = "tool_condition"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tool_items: Mapped[list["ToolItem"]] = relationship(back_populates="condition")
    loan_items: Mapped[list["LoanItem"]] = relationship(back_populates="return_condition")