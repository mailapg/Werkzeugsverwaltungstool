from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.security import get_current_user, require_role
from src.app.db.deps import get_db
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate, UserRead
import src.app.crud.user as crud

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
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email address already in use")
    return crud.create_user(db, data)


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
    return crud.update_user(db, user, data)


@router.delete("/deleteuser/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("ADMIN")),
):
    """Only ADMIN may delete user accounts."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user)
