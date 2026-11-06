
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey
)
from datetime import datetime

from backend.database import Base


class Complaint(Base):

    __tablename__ = "complaints"

    # Unique complaint ID
    id = Column(Integer, primary_key=True, index=True)

    # Citizen who submitted the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Complaint details
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)

    # ML prediction details
    category = Column(String(100), nullable=True)
    predicted_category = Column(String(100), nullable=True)
    prediction_confidence = Column(Float, nullable=True)

    # Location details
    location = Column(String(200), nullable=False)
    ward = Column(String(100), nullable=True)

    # GPS coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Incident and photograph details
    incident_datetime = Column(DateTime, nullable=True)
    photo_filename = Column(String(255), nullable=True)

    # Department and complaint status
    department = Column(String(100), nullable=True)
    status = Column(String(50), default="Submitted")

    # Submission date and time
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    location = Column(String(200), nullable=True)
    role = Column(String(20), default="citizen", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=True
    )

    message = Column(Text, nullable=False)

    is_read = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
