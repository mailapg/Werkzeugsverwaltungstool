import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.models.role import Role
from src.app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
import src.app.crud.department as crud
import src.app.crud.user as crud_user

router = APIRouter(tags=["Departments"])


@router.get("/getdepartments", response_model=list[DepartmentRead],
            dependencies=[Depends(get_current_user)])
def list_departments(db: Session = Depends(get_db)):
    return crud.get_departments(db)


@router.get("/getdepartment/{department_id}", response_model=DepartmentRead,
            dependencies=[Depends(get_current_user)])
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("/createdepartment", response_model=DepartmentRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_department(data: DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, data)


@router.patch("/updatedepartment/{department_id}", response_model=DepartmentRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_department(department_id: int, data: DepartmentUpdate, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if "lead_user_id" in data.model_fields_set:
        new_lead_id = data.lead_user_id
        old_lead_id = department.lead_user_id

        role_manager = db.query(Role).filter(Role.name == "DEPARTMENT_MANAGER").first()
        role_employee = db.query(Role).filter(Role.name == "EMPLOYEE").first()

        if new_lead_id is not None:
            conflict = crud.get_department_by_lead(db, new_lead_id)
            if conflict and conflict.id != department_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"User {new_lead_id} ist bereits Abteilungsleiter von '{conflict.name}'",
                )
            new_lead = crud_user.get_user(db, new_lead_id)
            if not new_lead:
                raise HTTPException(status_code=404, detail=f"User {new_lead_id} nicht gefunden")

            # Alten Leiter auf EMPLOYEE zurücksetzen (falls ein anderer gesetzt wird)
            if old_lead_id and old_lead_id != new_lead_id:
                old_lead = crud_user.get_user(db, old_lead_id)
                if old_lead and role_employee:
                    old_lead.role_id = role_employee.id

            # Neuen Leiter auf DEPARTMENT_MANAGER setzen und Abteilung zuweisen
            if role_manager:
                new_lead.role_id = role_manager.id
            new_lead.department_id = department_id

        else:
            # lead_user_id explizit auf null gesetzt → alten Leiter zurücksetzen
            if old_lead_id:
                old_lead = crud_user.get_user(db, old_lead_id)
                if old_lead and role_employee:
                    old_lead.role_id = role_employee.id
                # Zufälligen anderen Mitarbeiter der Abteilung zum neuen Leiter befördern
                candidates = [
                    u for u in crud_user.get_users_by_department(db, department_id)
                    if u.id != old_lead_id
                ]
                if candidates and role_manager:
                    new_auto_lead = random.choice(candidates)
                    new_auto_lead.role_id = role_manager.id
                    data.lead_user_id = new_auto_lead.id

    return crud.update_department(db, department, data)


@router.delete("/deletedepartment/{department_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    members = crud_user.get_users_by_department(db, department_id)
    if members:
        other_depts = [d for d in crud.get_departments(db) if d.id != department_id]
        if not other_depts:
            raise HTTPException(
                status_code=409,
                detail="Abteilung kann nicht gelöscht werden: keine andere Abteilung für die Mitglieder vorhanden",
            )
        role_employee = db.query(Role).filter(Role.name == "EMPLOYEE").first()
        for user in members:
            user.department_id = random.choice(other_depts).id
            if user.id == department.lead_user_id and role_employee:
                user.role_id = role_employee.id
        db.flush()

    name = department.name
    crud.delete_department(db, department)
    return {"message": f"Abteilung '{name}' wurde gelöscht", "id": department_id}
