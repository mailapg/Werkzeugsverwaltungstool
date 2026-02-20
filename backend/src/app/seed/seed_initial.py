from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.app.db.session import SessionLocal
from src.app.models import (
    Role,
    Department,
    User,
    ToolStatus,
    ToolCondition,
    ToolCategory,
    LoanRequestStatus,
    ToolItemIssueStatus,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_or_create(session: Session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    params = {**kwargs, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    session.flush()
    return instance


def run_seed():
    db: Session = SessionLocal()
    try:
        # --- Roles
        roles = ["ADMIN", "DEPARTMENT_MANAGER", "EMPLOYEE"]
        role_map = {name: get_or_create(db, Role, name=name) for name in roles}

        # --- Tool Status
        for status_name in ["AVAILABLE", "LOANED", "DEFECT", "MAINTENANCE", "RETIRED"]:
            get_or_create(db, ToolStatus, name=status_name)

        # --- Tool Condition
        for condition_name in ["OK", "WORN", "DEFECT"]:
            get_or_create(db, ToolCondition, name=condition_name)

        # --- Loan Request Status
        for rs_name in ["REQUESTED", "APPROVED", "REJECTED", "CANCELLED"]:
            get_or_create(db, LoanRequestStatus, name=rs_name)

        # --- Tool Item Issue Status (NEW)
        for issue_status_name in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]:
            get_or_create(db, ToolItemIssueStatus, name=issue_status_name)

        # --- Department (lead_user_id is nullable -> create department first)
        dep = get_or_create(db, Department, name="Werkstatt")

        # --- Create leader user for that department
        leader = get_or_create(
            db,
            User,
            email="jmueller@werkstatt.local",
            defaults=dict(
                firstname="Jonathan",
                lastname="Müller",
                passwordhash=pwd_context.hash("Passwort123!"),
                role_id=role_map["DEPARTMENT_MANAGER"].id,
                department_id=dep.id,
                is_active=True,
            ),
        )

        # --- Assign leader to department
        dep.lead_user_id = leader.id
        db.add(dep)

        db.commit()
        print("✅ Seed erfolgreich.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()