
import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserSession


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

SESSION_COOKIE = "civicconnect_session"
SESSION_DAYS = 7


# ---------------- PASSWORD FUNCTIONS ----------------

def hash_password(password):
    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        310000
    ).hex()

    return f"{salt}${hashed}"


def verify_password(password, stored_hash):
    try:
        salt, expected_hash = stored_hash.split("$")

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            310000
        ).hex()

        return secrets.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


# ---------------- SESSION FUNCTIONS ----------------

def make_session(response, user, db):
    token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=SESSION_DAYS)
    )

    db.add(session)
    db.commit()

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=SESSION_DAYS * 24 * 60 * 60,
        path="/"
    )


def get_logged_in_user(request, db):
    token = request.cookies.get(SESSION_COOKIE)

    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash
    ).first()

    if not session:
        return None

    if session.expires_at <= datetime.utcnow():
        db.delete(session)
        db.commit()
        return None

    return db.query(User).filter(
        User.id == session.user_id
    ).first()


def user_data(user):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "location": user.location,
        "role": user.role
    }


# ---------------- REQUEST MODELS ----------------

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str
    phone: str = Field(min_length=7, max_length=15)
    password: str = Field(min_length=8)
    confirm_password: str
    location: str = Field(default="", max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------- CITIZEN REGISTRATION ----------------

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    if "@" not in email or "." not in email.split("@")[-1]:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Enter a valid email address."
            }
        )

    if data.password != data.confirm_password:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Passwords do not match.",
                "fields": {
                    "confirm_password": "Passwords do not match."
                }
            }
        )

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        return JSONResponse(
            status_code=409,
            content={
                "error": "An account with this email already exists.",
                "fields": {
                    "email": "Email already registered."
                }
            }
        )

    user = User(
        full_name=data.full_name.strip(),
        email=email,
        phone=data.phone.strip(),
        password_hash=hash_password(data.password),
        location=data.location.strip(),
        role="citizen"
    )

    db.add(user)
    db.commit()

    return {
        "message": "Account created successfully."
    }


# ---------------- CITIZEN LOGIN ----------------

@router.post("/login")
def citizen_login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email.strip().lower()
    ).first()

    if not user or user.role != "citizen":
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid email or password."
            }
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid email or password."
            }
        )

    make_session(response, user, db)

    return {
        "user": user_data(user)
    }


# ---------------- ADMIN LOGIN ----------------

@router.post("/admin-login")
def admin_login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == data.email.strip().lower()
    ).first()

    if not user or user.role != "admin":
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid administrator credentials."
            }
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        return JSONResponse(
            status_code=401,
            content={
                "error": "Invalid administrator credentials."
            }
        )

    make_session(response, user, db)

    return {
        "user": user_data(user)
    }


# ---------------- CURRENT USER ----------------

@router.get("/me")
def current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_logged_in_user(request, db)

    if not user:
        return {
            "user": None
        }

    return {
        "user": user_data(user)
    }


# ---------------- LOGOUT ----------------

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    token = request.cookies.get(SESSION_COOKIE)

    if token:
        token_hash = hashlib.sha256(
            token.encode()
        ).hexdigest()

        session = db.query(UserSession).filter(
            UserSession.token_hash == token_hash
        ).first()

        if session:
            db.delete(session)
            db.commit()

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax"
    )

    return {
        "message": "Logged out successfully."
    }
