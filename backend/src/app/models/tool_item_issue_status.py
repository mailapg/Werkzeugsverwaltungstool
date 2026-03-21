from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ToolItemIssueStatus(Base):
    __tablename__ = "tool_item_issue_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    issues: Mapped[list["ToolItemIssue"]] = relationship(back_populates="status")