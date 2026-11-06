
from getpass import getpass

from backend.database import SessionLocal
from backend.models import User
from backend.routes.auth import hash_password


db = SessionLocal()

try:
    print("Create CivicConnect Admin Account")

    full_name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    phone = input("Admin phone: ").strip()
    password = getpass("Create password (minimum 8 characters): ")
    confirm_password = getpass("Confirm password: ")

    if not full_name or not email or not phone:
        print("All details are required.")
    elif len(password) < 8:
        print("Password must contain at least 8 characters.")
    elif password != confirm_password:
        print("Passwords do not match.")
    elif db.query(User).filter(User.email == email).first():
        print("An account with this email already exists.")
    else:
        admin = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            location="",
            role="admin"
        )

        db.add(admin)
        db.commit()

        print("Admin account created successfully!")

finally:
    db.close()
