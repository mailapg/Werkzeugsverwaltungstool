# ============================================================
# security.py – Sicherheitsfunktionen: Passwort, Benutzeridentität, Rollenprüfung
#
# Enthält:
#   - Passwort-Verifikation (bcrypt)
#   - get_current_user: FastAPI-Dependency, die aus dem Token den eingeloggten User liest
#   - require_role: Factory-Dependency, die den Zugriff auf bestimmte Rollen beschränkt
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.app.auth.jwt import decode_token
from src.app.db.deps import get_db
from src.app.models.user import User

# bcrypt-Kontext für Passwort-Hashing und -Verifikation.
# bcrypt ist ein bewährter Algorithmus, der Passwörter absichtlich langsam hasht,
# um Brute-Force-Angriffe zu erschweren. deprecated="auto" aktualisiert alte Hashes automatisch.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer: Liest den Bearer-Token aus dem Authorization-Header.
# tokenUrl zeigt auf den Login-Endpunkt (wird nur für die Swagger-UI-Dokumentation benötigt).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    """Vergleicht ein Klartext-Passwort mit einem bcrypt-Hash."""
    return pwd_context.verify(plain, hashed)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI-Dependency – wird in jedem geschützten Endpunkt verwendet.

    Ablauf:
      1. Bearer-Token aus dem Authorization-Header lesen
      2. JWT-Signatur und Ablaufzeit prüfen
      3. Prüfen ob Token gesperrt (Blacklist, nach Logout)
      4. Benutzer aus der Datenbank laden
      5. Prüfen ob Benutzer aktiv ist

    Returns:
        Den eingeloggten User (SQLAlchemy-Objekt)

    Raises:
        401 Unauthorized: Wenn Token ungültig, abgelaufen oder gesperrt ist
    """
    # Standard-Fehler für alle Authentifizierungsprobleme
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Token entschlüsseln und Benutzer-ID auslesen
        payload = decode_token(token)
        user_id = payload.get("sub")  # "sub" ist der Standard-Claim für die User-ID
        if user_id is None:
            raise exc
    except JWTError:
        raise exc

    # Prüfen ob Token durch Logout gesperrt wurde
    from src.app.crud.blacklisted_token import is_token_blacklisted
    if is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Benutzer aus der Datenbank laden und auf Aktiv-Status prüfen
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise exc
    return user


def require_role(*role_ids: int):
    """
    Erstellt eine FastAPI-Dependency zur Rollenprüfung.

    Verwendung an einem Endpunkt:
        @router.post("/createuser", dependencies=[Depends(require_role(ADMIN_ID))])
        @router.patch("/decide/{id}", dependencies=[Depends(require_role(ADMIN_ID, MANAGER_ID))])

    Wirft HTTP 403 Forbidden, wenn der eingeloggte Benutzer keine der erlaubten Rollen hat.
    """
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role_id not in role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return _dependency
