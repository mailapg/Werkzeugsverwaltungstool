import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.models.user import User
from src.app.models.role import Role
from src.app.models.department import Department
from src.app.schemas.user import UserCreate, UserUpdate, UserRead
import src.app.crud.user as crud
import src.app.crud.department as crud_dept

router = APIRouter(tags=["Users"])


@router.get("/getusers", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return crud.get_users(db)


@router.get("/getuser/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/createuser", response_model=UserRead, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
):
    """Only ADMIN may create new user accounts."""
    role = db.get(Role, data.role_id)
    if not role:
        raise HTTPException(status_code=404, detail=f"Rolle mit ID {data.role_id} nicht gefunden")
    dept = db.get(Department, data.department_id)
    if not dept:
        raise HTTPException(status_code=404, detail=f"Abteilung mit ID {data.department_id} nicht gefunden")
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email address already in use")

    new_user = crud.create_user(db, data)

    # Wenn neuer Nutzer DEPARTMENT_MANAGER ist → alten Leiter der Abteilung demoten
    if role.name == "DEPARTMENT_MANAGER":
        role_employee = db.query(Role).filter(Role.name == "EMPLOYEE").first()
        if dept.lead_user_id and dept.lead_user_id != new_user.id:
            old_lead = crud.get_user(db, dept.lead_user_id)
            if old_lead and role_employee:
                old_lead.role_id = role_employee.id
        dept.lead_user_id = new_user.id
        db.commit()
        db.refresh(new_user)

    return new_user


@router.patch("/updateuser/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
):
    """Only ADMIN may update user accounts."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.email:
        existing = crud.get_user_by_email(db, data.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail="Email address already in use")

    if "role_id" in data.model_fields_set or "department_id" in data.model_fields_set:
        current_role = db.get(Role, user.role_id)
        new_role = db.get(Role, data.role_id if "role_id" in data.model_fields_set else user.role_id)
        old_dept_id = user.department_id
        new_dept_id = data.department_id if "department_id" in data.model_fields_set else user.department_id

        role_manager = db.query(Role).filter(Role.name == "DEPARTMENT_MANAGER").first()
        role_employee = db.query(Role).filter(Role.name == "EMPLOYEE").first()

        was_manager = current_role and current_role.name == "DEPARTMENT_MANAGER"
        becomes_manager = new_role and new_role.name == "DEPARTMENT_MANAGER"
        dept_changed = old_dept_id != new_dept_id

        # Nutzer verlässt Abteilungsleiter-Position (Rolle-Wechsel weg oder Abteilung wechselt)
        if was_manager and (not becomes_manager or dept_changed):
            old_dept = crud_dept.get_department_by_lead(db, user_id)
            if old_dept:
                candidates = [u for u in crud.get_users_by_department(db, old_dept.id) if u.id != user_id]
                if candidates and role_manager:
                    new_lead = random.choice(candidates)
                    new_lead.role_id = role_manager.id
                    old_dept.lead_user_id = new_lead.id
                else:
                    old_dept.lead_user_id = None

        # Nutzer wird Abteilungsleiter (Rolle wird MANAGER oder wechselt als MANAGER in neue Abteilung)
        if becomes_manager and (not was_manager or dept_changed):
            new_dept = db.get(Department, new_dept_id)
            if new_dept:
                if new_dept.lead_user_id and new_dept.lead_user_id != user_id:
                    old_lead = crud.get_user(db, new_dept.lead_user_id)
                    if old_lead and role_employee:
                        old_lead.role_id = role_employee.id
                new_dept.lead_user_id = user_id

        db.flush()

    return crud.update_user(db, user, data)


@router.delete("/deleteuser/{user_id}", status_code=200)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
):
    """Only ADMIN may delete user accounts."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Wenn der Nutzer Abteilungsleiter ist → zufälligen Nachfolger befördern
    dept = crud_dept.get_department_by_lead(db, user_id)
    if dept:
        role_manager = db.query(Role).filter(Role.name == "DEPARTMENT_MANAGER").first()
        candidates = [
            u for u in crud.get_users_by_department(db, dept.id)
            if u.id != user_id
        ]
        if candidates and role_manager:
            new_lead = random.choice(candidates)
            new_lead.role_id = role_manager.id
            dept.lead_user_id = new_lead.id
        else:
            dept.lead_user_id = None
        db.flush()

    name = f"{user.firstname} {user.lastname}"
    crud.delete_user(db, user)
    return {"message": f"Benutzer '{name}' wurde gelöscht", "id": user_id}
