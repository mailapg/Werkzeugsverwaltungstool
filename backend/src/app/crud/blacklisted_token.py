from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.app.models.blacklisted_token import BlacklistedToken


def blacklist_token(db: Session, token: str, expires_at: datetime) -> BlacklistedToken:
    entry = BlacklistedToken(token=token, expires_at=expires_at)
    db.add(entry)
    db.commit()
    return entry


def is_token_blacklisted(db: Session, token: str) -> bool:
    return (
        db.query(BlacklistedToken)
        .filter(BlacklistedToken.token == token)
        .first()
        is not None
    )


def cleanup_expired_tokens(db: Session) -> None:
    """Removes expired tokens from the blacklist – call this periodically."""
    now = datetime.now(tz=timezone.utc)
    db.query(BlacklistedToken).filter(BlacklistedToken.expires_at < now).delete()
    db.commit()
