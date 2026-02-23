from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.role import Role
from src.app.schemas.role import RoleCreate, RoleUpdate


def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.get(Role, role_id)


def get_roles(db: Session) -> list[Role]:
    return db.query(Role).all()


def create_role(db: Session, data: RoleCreate) -> Role:
    role = Role(**data.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, role: Role, data: RoleUpdate) -> Role:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(role, field, value)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()
