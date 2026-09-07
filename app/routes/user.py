from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException
)
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import (
    get_current_user,
    require_admin
)
from app.models.user import User
from app.schemas.auth import (
    UserUpdate,
    UserPatch
)
from app.services import user as user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    )
):

    return user_service.get_my_profile(
        current_user
    )

@router.put("/me")
def update_my_profile(
    data: UserUpdate,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return user_service.update_my_profile(
        data,
        current_user,
        db
    )

@router.patch("/me")
def patch_my_profile(
    data: UserPatch,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return user_service.patch_my_profile(
        data,
        current_user,
        db
    )

@router.delete("/me")
def delete_my_profile(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        get_current_user
    )
):

    return user_service.delete_my_profile(
        current_user,
        db
    )

@router.get("/search")
def search_users(
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_admin
    )
):

    return user_service.search_users(
        name,
        email,
        phone,
        db
    )

@router.get("/{email}")
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return user_service.get_user_by_email(
        email=email,
        db=db
    )

@router.get("/")
def get_all_users(
    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_admin
    )
):

    return user_service.get_all_users(
        db
    )

@router.delete("/")
def delete_all_users(
    response: Response,

    db: Session = Depends(
        get_db
    ),

    current_user: User = Depends(
        require_admin
    )
):

    result = user_service.delete_all_users(
        db
    )

    response.delete_cookie(
        "session_id"
    )

    response.delete_cookie(
        "access_token"
    )

    return result