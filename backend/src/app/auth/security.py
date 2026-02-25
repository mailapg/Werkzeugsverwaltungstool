"""Security dependencies: password verification, current-user resolution, role guard."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.app.auth.jwt import decode_token
from src.app.db.deps import get_db
from src.app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Points Swagger UI to the login endpoint for the "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency – validates Bearer token and returns the active User."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise exc
    except JWTError:
        raise exc

    from src.app.crud.blacklisted_token import is_token_blacklisted
    if is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise exc
    return user


def require_role(*roles: str):
    """
    Returns a FastAPI dependency that enforces role-based access.

    Usage:
        @router.post("/createuser", dependencies=[Depends(require_role("ADMIN"))])
    """
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _dependency
