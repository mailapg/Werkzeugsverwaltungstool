"""Authentication router – login and logout."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.app.auth.jwt import create_access_token, decode_token
from src.app.auth.security import oauth2_scheme, verify_password
from src.app.crud.blacklisted_token import blacklist_token
from src.app.crud.user import get_user_by_email
from src.app.db.deps import get_db
from src.app.schemas.token import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Login with email (username field) and password.
    Returns a JWT Bearer token on success.
    """
    user = get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.passwordhash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    token_data = {
        "sub": str(user.id),
        "role": user.role.name,
        "department_id": user.department_id,
    }
    return TokenResponse(
        access_token=create_access_token(token_data),
        token_type="bearer",
    )


@router.post("/logout", status_code=204)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> None:
    """
    Invalidates the current Bearer token by adding it to the blacklist.
    Subsequent requests with this token will be rejected with 401.
    """
    payload = decode_token(token)
    exp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    blacklist_token(db, token, expires_at)
