from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)

from app.services import auth as auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    return auth_service.register_user(
        user_data,
        db
    )

@router.post("/login")
def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    return auth_service.login_user(
        login_data,
        response,
        db
    )

@router.post("/logout")
def logout(
    response: Response,

    session_id: str | None = Cookie(
        default=None
    ),

    access_token: str | None = Cookie(
        default=None
    ),

    refresh_token: str | None = Cookie(
        default=None
    ),

    db: Session = Depends(get_db)
):
    return auth_service.logout_user(
        response,
        session_id,
        access_token,
        refresh_token,
        db
    )

@router.post("/refresh-token")
def refresh_token(
    response: Response,

    refresh_token: str | None = Cookie(
        default=None
    ),

    db: Session = Depends(get_db)
):
    return auth_service.refresh_access_token(
        response,
        refresh_token,
        db
    )

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return auth_service.forgot_password(
        data,
        background_tasks,
        db
    )

@router.post("/verify-otp")
def verify_password_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    return auth_service.verify_password_otp(
        data,
        db
    )

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return auth_service.reset_password(
        data,
        db
    )
