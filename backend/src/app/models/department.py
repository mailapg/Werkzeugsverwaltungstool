from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # NULL erlaubt (sonst Insert-Zirkel bei initialem Setup)
    lead_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=True,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="department",
        foreign_keys="User.department_id",
    )

    lead_user: Mapped[Optional["User"]] = relationship(
        foreign_keys=[lead_user_id],
        post_update=True,
    )