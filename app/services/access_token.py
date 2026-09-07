import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.access_token import AccessToken


def hash_token(token: str) -> str:

    return hashlib.sha256(
        token.encode()
    ).hexdigest()

def save_access_token(
    db: Session,
    user_id: str,
    token: str,
    expires_at: datetime,
    token_type: str = "access"
):

    token_hash = hash_token(token)

    access_token = AccessToken(
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at
    )

    db.add(access_token)
    db.commit()
    db.refresh(access_token)

    return access_token

def get_access_token(
    db: Session,
    token: str
):

    token_hash = hash_token(token)

    return (
        db.query(AccessToken)
        .filter(
            AccessToken.token_hash == token_hash
        )
        .first()
    )

def delete_access_token(
    db: Session,
    token: str
):

    token_record = get_access_token(
        db,
        token
    )

    if token_record:

        db.delete(token_record)
        db.commit()

def delete_user_access_tokens(
    db: Session,
    user_id: str
):

    db.query(AccessToken).filter(
        AccessToken.user_id == user_id
    ).delete()

    db.commit()
