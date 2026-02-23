from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.db.deps import get_db
from src.app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
import src.app.crud.department as crud

router = APIRouter(tags=["Departments"])


@router.get("/getdepartments", response_model=list[DepartmentRead])
def list_departments(db: Session = Depends(get_db)):
    return crud.get_departments(db)


@router.get("/getdepartment/{department_id}", response_model=DepartmentRead)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("/createdepartment", response_model=DepartmentRead, status_code=201)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, data)


@router.patch("/updatedepartment/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, data: DepartmentUpdate, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return crud.update_department(db, department, data)


@router.delete("/deletedepartment/{department_id}", status_code=204)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    crud.delete_department(db, department)
