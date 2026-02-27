from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import require_role
from src.app.db.deps import get_db
from src.app.schemas.role import RoleCreate, RoleUpdate, RoleRead
import src.app.crud.role as crud

router = APIRouter(tags=["Roles"])


@router.get("/getroles", response_model=list[RoleRead],
            dependencies=[Depends(require_role("ADMIN"))])
def list_roles(db: Session = Depends(get_db)):
    return crud.get_roles(db)


@router.get("/getrole/{role_id}", response_model=RoleRead,
            dependencies=[Depends(require_role("ADMIN"))])
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/createrole", response_model=RoleRead, status_code=201,
             dependencies=[Depends(require_role("ADMIN"))])
def create_role(data: RoleCreate, db: Session = Depends(get_db)):
    return crud.create_role(db, data)


@router.patch("/updaterole/{role_id}", response_model=RoleRead,
              dependencies=[Depends(require_role("ADMIN"))])
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return crud.update_role(db, role, data)


@router.delete("/deleterole/{role_id}", status_code=200,
               dependencies=[Depends(require_role("ADMIN"))])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    crud.delete_role(db, role)
    return {"message": f"Rolle '{role.name}' wurde gelöscht", "id": role_id}
