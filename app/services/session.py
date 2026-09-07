import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.session import UserSession


SESSION_EXPIRE_MINUTES = 60


def create_session(
    db: Session,
    user_id: str
):

    session_id = secrets.token_urlsafe(64)

    expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=SESSION_EXPIRE_MINUTES
        )
    )

    session = UserSession(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session_id

def get_session(
    db: Session,
    session_id: str
):

    session = (
        db.query(UserSession)
        .filter(
            UserSession.session_id == session_id
        )
        .first()
    )

    if not session:
        return None

    if session.expires_at < datetime.utcnow():

        db.delete(session)
        db.commit()

        return None

    return session

def delete_session(
    db: Session,
    session_id: str
):

    session = (
        db.query(UserSession)
        .filter(
            UserSession.session_id == session_id
        )
        .first()
    )

    if session:

        db.delete(session)
        db.commit()

def delete_user_sessions(
    db: Session,
    user_id: str
):

    sessions = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user_id
        )
        .all()
    )

    for session in sessions:
        db.delete(session)

    db.commit()