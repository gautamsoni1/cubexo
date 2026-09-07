from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserUpdate, UserPatch

from app.services.auth import hash_password
from app.services.session import delete_user_sessions
from app.services.access_token import delete_user_access_tokens


def get_user_response(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "phone": user.phone,
        "email": user.email
    }

def get_my_profile(
    current_user: User
):
    return get_user_response(current_user)

def update_my_profile(
    data: UserUpdate,
    current_user: User,
    db: Session
):
    existing_email = (
        db.query(User)
        .filter(
            User.email == data.email,
            User.id != current_user.id
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
            User.phone == data.phone,
            User.id != current_user.id
        )
        .first()
    )

    if existing_phone:
        raise HTTPException(
            status_code=409,
            detail="Phone number already registered"
        )

    current_user.name = data.name
    current_user.surname = data.surname
    current_user.phone = data.phone
    current_user.email = data.email
    current_user.password = hash_password(
        data.password
    )

    db.commit()
    db.refresh(current_user)

    return {
        "message": "User profile replaced successfully",
        "user": get_user_response(current_user)
    }

def patch_my_profile(
    data: UserPatch,
    current_user: User,
    db: Session
):
    if data.email is None:
        return {
            "message": "No changes provided",
            "user": get_user_response(current_user)
        }

    existing_email = (
        db.query(User)
        .filter(
            User.email == data.email,
            User.id != current_user.id
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    current_user.email = data.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Email updated successfully",
        "user": get_user_response(current_user)
    }

def delete_my_profile(
    current_user: User,
    db: Session
):
    delete_user_sessions(
        db,
        current_user.id
    )

    delete_user_access_tokens(
        db,
        current_user.id
    )

    db.delete(current_user)
    db.commit()

    return {
        "message": "User account deleted successfully"
    }

def search_users(
    name: str | None,
    email: str | None,
    phone: str | None,
    db: Session
):
    query = db.query(User)

    if name:
        query = query.filter(
            User.name.ilike(f"%{name}%")
        )

    if email:
        query = query.filter(
            User.email.ilike(f"%{email}%")
        )

    if phone:
        query = query.filter(
            User.phone.ilike(f"%{phone}%")
        )

    users = query.all()

    return {
        "count": len(users),
        "users": [
            get_user_response(user)
            for user in users
        ]
    }

def get_user_by_email(
    email: str,
    db: Session
):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "phone": user.phone,
        "email": user.email,
        "role": user.role
    }

def get_all_users(
    db: Session
):
    users = db.query(User).all()

    return {
        "count": len(users),
        "users": [
            get_user_response(user)
            for user in users
        ]
    }

def delete_all_users(
    db: Session
):
    users = db.query(User).all()

    if not users:
        return {
            "message": "No users found",
            "deleted_count": 0
        }

    deleted_count = len(users)

    for user in users:
        delete_user_sessions(
            db,
            user.id
        )

        delete_user_access_tokens(
            db,
            user.id
        )

    db.query(User).delete(
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "All users deleted successfully",
        "deleted_count": deleted_count
    }