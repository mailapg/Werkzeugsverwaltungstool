from typing import Optional
from sqlalchemy.orm import Session

from src.app.models.department import Department
from src.app.schemas.department import DepartmentCreate, DepartmentUpdate


def get_department(db: Session, department_id: int) -> Optional[Department]:
    return db.get(Department, department_id)


def get_departments(db: Session) -> list[Department]:
    return db.query(Department).all()


def get_department_by_lead(db: Session, lead_user_id: int) -> Optional[Department]:
    return db.query(Department).filter(Department.lead_user_id == lead_user_id).first()


def create_department(db: Session, data: DepartmentCreate) -> Department:
    department = Department(**data.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def update_department(db: Session, department: Department, data: DepartmentUpdate) -> Department:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return department


def delete_department(db: Session, department: Department) -> None:
    db.delete(department)
    db.commit()
