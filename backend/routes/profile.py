
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, Complaint
from backend.routes.auth import (
    get_logged_in_user,
    hash_password,
    verify_password
)

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"]
)


# Profile update request
class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    location: str = Field(min_length=2, max_length=200)


# Password change request
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str


# Get logged-in citizen
def get_citizen(request, db):
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in as a citizen."
        )

    return user


# 1. Get profile details
@router.get("")
def get_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_citizen(request, db)

    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "location": user.location
        }
    }


# 2. Update profile details
@router.put("")
def update_profile(
    data: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_citizen(request, db)

    user.full_name = data.full_name.strip()
    user.phone = data.phone.strip()
    user.location = data.location.strip()

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully."
    }


# 3. Change password
@router.post("/change-password")
def change_password(
    data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_citizen(request, db)

    if not verify_password(
        data.current_password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect."
        )

    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New passwords do not match."
        )

    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different."
        )

    user.password_hash = hash_password(data.new_password)

    db.commit()

    return {
        "message": "Password changed successfully."
    }
