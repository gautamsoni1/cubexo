from urllib import request

import bcrypt

from datetime import (
    datetime,
    timedelta
)

from fastapi import (
    BackgroundTasks,
    HTTPException,
    Response,
    status
)

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.otp import PasswordOTP

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest
)

from app.config.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

from app.services.session import (
    create_session,
    delete_session,
    delete_user_sessions
)

from app.services.access_token import (
    save_access_token,
    get_access_token,
    delete_access_token
)

from app.services.otp import create_otp
from app.services.email import send_otp_email
from app.services.otp import verify_otp



def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:

        raise ValueError(
            "Password cannot be longer than 72 bytes"
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def register_user(
    user_data: RegisterRequest,
    db: Session
):

    existing_email = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_email:

        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    existing_phone = (
        db.query(User)
        .filter(
            User.phone == user_data.phone
        )
        .first()
    )

    if existing_phone:

        raise HTTPException(
            status_code=409,
            detail="Phone number already registered"
        )

    hashed_password = hash_password(
        user_data.password
    )

    user = User(
        name=user_data.name,
        surname=user_data.surname,
        phone=user_data.phone,
        email=user_data.email,
        password=hashed_password,
        role="user",
        pincode=user_data.pincode
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "role": user.role
    }

def login_user(
    login_data: LoginRequest,
    response: Response,
    db: Session
):

    user = (
        db.query(User)
        .filter(
            User.email == login_data.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    session_id = create_session(
        db,
        user.id
    )

    access_token = create_access_token(
        user.id
    )

    refresh_token = create_refresh_token(
        user.id
    )

    access_token_expires = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    refresh_token_expires = (
        datetime.utcnow()
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    save_access_token(
        db=db,
        user_id=user.id,
        token=access_token,
        expires_at=access_token_expires,
        token_type="access"
    )

    save_access_token(
        db=db,
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires,
        token_type="refresh"
    )

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * REFRESH_TOKEN_EXPIRE_DAYS
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

def logout_user(
    response: Response,
    session_id: str | None,
    access_token: str | None,
    refresh_token: str | None,
    db: Session
):


    if session_id:

        delete_session(
            db,
            session_id
        )


    if access_token:

        delete_access_token(
            db,
            access_token
        )

    if refresh_token:

        delete_access_token(
            db,
            refresh_token
        )


    response.delete_cookie(
        key="session_id"
    )

    response.delete_cookie(
        key="access_token"
    )

    response.delete_cookie(
        key="refresh_token"
    )

    return {
        "message": "Logout successful"
    }

def refresh_access_token(
    response: Response,
    refresh_token: str | None,
    db: Session
):

    if not refresh_token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required"
        )

    token_record = get_access_token(
        db,
        refresh_token
    )

    if not token_record:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    if token_record.expires_at < datetime.utcnow():

        delete_access_token(
            db,
            refresh_token
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    jwt_user_id = verify_refresh_token(
        refresh_token
    )

    if jwt_user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
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

    access_token = create_access_token(
        user.id
    )

    access_token_expires = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    save_access_token(
        db=db,
        user_id=user.id,
        token=access_token,
        expires_at=access_token_expires,
        token_type="access"
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )

    return {
        "message": "Access token refreshed successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }

def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session
):

    user = (
        db.query(User)
        .filter(
            User.email == data.email
        )
        .first()
    )

    if not user:

        return {
            "message": (
                "If this email is registered, "
                "an OTP has been sent"
            )
        }

    otp = create_otp(
        db,
        user.id
    )

    print(
        "OTP generated:",
        otp
    )

    background_tasks.add_task(
        send_otp_email,
        user.email,
        otp
    )


    return {
        "message": "OTP sent successfully"
    }

def verify_password_otp(
    data: VerifyOTPRequest,
    db: Session
):

    user = (
        db.query(User)
        .filter(
            User.email == data.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    valid = verify_otp(
        db,
        user.id,
        data.otp
    )

    if not valid:

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    return {
        "message": "OTP verified successfully"
    }

def reset_password(
    data: ResetPasswordRequest,
    db: Session
):

    user = (
        db.query(User)
        .filter(
            User.email == data.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=400,
            detail="Unable to reset password"
        )

    otp_record = (
        db.query(PasswordOTP)
        .filter(
            PasswordOTP.user_id == user.id,
            PasswordOTP.verified == True
        )
        .first()
    )
    if not otp_record:
        raise HTTPException(
            status_code=403,
            detail="OTP verification required"
        )
    if otp_record.expires_at < datetime.utcnow():

        raise HTTPException(
            status_code=403,
            detail="OTP verification expired"
        )
    user.password = hash_password(
        data.new_password
    )
    db.delete(
        otp_record
    )
    delete_user_sessions(
        db,
        user.id
    )
    db.commit()
    return {
        "message": (
            "Password updated successfully. "
            "Please login again."
        )
    }
