# ============================================================
# jwt.py – JWT-Token erstellen und lesen
#
# JWT (JSON Web Token) ist ein Standard zur sicheren Übertragung von
# Benutzerinformationen. Ein Token enthält:
#   - sub:           Benutzer-ID
#   - role_id:       Rolle (1=Admin, 2=Manager, 3=Employee)
#   - department_id: Abteilung des Benutzers
#   - exp:           Ablaufzeit des Tokens
#
# Der Token ist mit dem JWT_SECRET_KEY signiert. Ohne den geheimen Schlüssel
# kann niemand den Token fälschen oder verändern.
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

from src.app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erstellt einen signierten JWT-Token.

    Args:
        data: Dictionary mit den Token-Inhalten (muss mindestens 'sub' mit der User-ID enthalten)
        expires_delta: Optionale Gültigkeitsdauer (Standard: ACCESS_TOKEN_EXPIRE_MINUTES aus .env)

    Returns:
        Der signierte JWT als String (Format: header.payload.signature)
    """
    to_encode = data.copy()
    # Ablaufzeit berechnen und zum Token-Payload hinzufügen
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    # Token mit dem geheimen Schlüssel signieren
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Liest und verifiziert einen JWT-Token.

    Prüft:
      - Ist die Signatur gültig? (Wurde der Token nicht verändert?)
      - Ist der Token noch nicht abgelaufen?

    Returns:
        Den Payload des Tokens als Dictionary

    Raises:
        jose.JWTError: Wenn der Token ungültig oder abgelaufen ist
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
