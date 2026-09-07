from datetime import datetime

from fastapi import (
    Cookie,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.user import User

from app.config.jwt import (
    verify_access_token
)

from app.services.access_token import (
    get_access_token
)

bearer_scheme = HTTPBearer(
    auto_error=False
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),

    access_token: str | None = Cookie(
        default=None
    ),

    db: Session = Depends(
        get_db
    )
):
    """
    Authenticate the current user.

    Authentication supports:

    1. Swagger / Authorization Header
       Authorization: Bearer <token>

    2. Browser / Postman Cookie
       access_token=<token>
    """
    token = None

    if credentials:
        token = credentials.credentials

    if not token:
        token = access_token

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required"
        )

    token_record = get_access_token(
        db,
        token
    )

    if not token_record:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found"
        )

    if token_record.expires_at < datetime.utcnow():

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )

    jwt_user_id = verify_access_token(
        token
    )

    if jwt_user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    if token_record.user_id != jwt_user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication mismatch"
        )

    user = (
        db.query(User)
        .filter(
            User.id == jwt_user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def require_admin(
    current_user: User = Depends(
        get_current_user
    )
):
    """
    Allow only admin users.
    """

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user