import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import PasswordOTP

OTP_EXPIRE_MINUTES = 5


def generate_otp() -> str:

    return str(
        secrets.randbelow(1_000_000)
    ).zfill(6)

def create_otp(
    db: Session,
    user_id: str
):
    from app.services.auth import hash_password

    print("========== CREATE OTP START ==========")
    print("USER ID:", user_id)

    deleted_count = (
        db.query(PasswordOTP)
        .filter(
            PasswordOTP.user_id == user_id
        )
        .delete(
            synchronize_session=False
        )
    )

    print("OLD OTP DELETED:", deleted_count)

    otp = generate_otp()
    print("GENERATED OTP:", otp)

    otp_hash = hash_password(otp)
    print("OTP HASH CREATED")

    expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=OTP_EXPIRE_MINUTES
        )
    )

    otp_record = PasswordOTP(
        user_id=user_id,
        otp_hash=otp_hash,
        expires_at=expires_at,
        verified=False
    )

    print("OTP RECORD CREATED")
    print("USER ID:", otp_record.user_id)
    print("EXPIRES:", otp_record.expires_at)
    print("VERIFIED:", otp_record.verified)

    db.add(otp_record)
    print("ADDED TO SESSION")
    db.commit()
    print("COMMIT SUCCESSFUL")
    db.refresh(otp_record)

    print("DATABASE ID:", otp_record.id)

    print("========== CREATE OTP END ==========")

    return otp

def verify_otp(
    db: Session,
    user_id: str,
    otp: str
):
    from app.services.auth import verify_password

    otp_record = (
        db.query(PasswordOTP)
        .filter(
            PasswordOTP.user_id == user_id,
            PasswordOTP.verified == False
        )
        .first()
    )

    if not otp_record:
        return False

    if otp_record.expires_at < datetime.utcnow():

        db.delete(otp_record)
        db.commit()

        return False

    if not verify_password(
        otp,
        otp_record.otp_hash
    ):
        return False

    otp_record.verified = True

    db.commit()

    return True
