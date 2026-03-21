# ============================================================
# auth/router.py – Login und Logout Endpunkte
#
# POST /auth/login  → prüft Credentials, gibt JWT zurück
# POST /auth/logout → sperrt den aktuellen Token (Blacklist)
# ============================================================

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
    Login mit E-Mail (Feld 'username') und Passwort.

    Ablauf:
      1. Benutzer anhand der E-Mail in der DB suchen
      2. Passwort mit gespeichertem bcrypt-Hash vergleichen
      3. Prüfen ob der Account aktiv ist
      4. JWT-Token erstellen und zurückgeben

    Das Token enthält: Benutzer-ID, Rollen-ID, Abteilungs-ID

    Gibt HTTP 401 zurück wenn: E-Mail nicht gefunden, Passwort falsch, Account inaktiv
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

    # Token-Payload: Diese Infos werden im JWT gespeichert
    token_data = {
        "sub": str(user.id),          # Benutzer-ID (Standard: "subject")
        "role_id": user.role_id,       # Für Rollenprüfung im Frontend
        "department_id": user.department_id,  # Für Datenfiltierung nach Abteilung
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
    Logout: Sperrt den aktuellen Token durch Eintrag in die Blacklist.

    Da JWTs zustandslos sind, kann man sie nicht "löschen".
    Stattdessen wird der Token in der blacklisted_tokens-Tabelle gespeichert.
    Bei jeder Anfrage prüft get_current_user ob der Token gesperrt ist.
    Der Token wird mit seiner originalen Ablaufzeit gespeichert,
    damit abgelaufene Einträge irgendwann bereinigt werden können.
    """
    payload = decode_token(token)
    exp = payload.get("exp")  # Unix-Timestamp der Ablaufzeit
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    blacklist_token(db, token, expires_at)
