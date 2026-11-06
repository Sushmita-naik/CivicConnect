
from pathlib import Path
from datetime import datetime
import uuid
import re

import joblib

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Form,
    File,
    UploadFile
)
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas
from backend.routes.auth import get_logged_in_user


# Load the trained ML model
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "complaint_pipeline_383.pkl"
)

pipeline = joblib.load(MODEL_PATH)


# Photo storage directory
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Allowed photo formats
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp"
}

MAX_PHOTO_SIZE = 5 * 1024 * 1024


# Create router
router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


# Department mapping
DEPARTMENT_MAPPING = {
    "Road Damage": "Road Maintenance Department",
    "Garbage / Waste": "Sanitation Department",
    "Streetlight": "Electrical Department",
    "Water Leakage": "Water Supply Department",
    "Drainage / Sewer Issue": "Drainage Department"
}


# Convert frontend category names to backend categories
CATEGORY_MAPPING = {
    "Garbage": "Garbage / Waste",
    "Drainage": "Drainage / Sewer Issue"
}


# 1. Submit a complaint
@router.post("/")
async def create_complaint(
    request: Request,
    title: str = Form(""),
    description: str = Form(...),
    category: str = Form(""),
    predicted_category: str = Form(""),
    prediction_confidence: str = Form(""),
    incident_datetime: str = Form(""),
    location: str = Form(...),
    ward: str = Form(""),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):

    # Identify logged-in citizen
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in as a citizen."
        )

    # Validate complaint details
    title = title.strip()
    description = description.strip()
    location = location.strip()
    ward = ward.strip()

    if len(description) < 5 or len(description) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Description must contain 5 to 2000 characters."
        )

    if len(title) > 200 or len(location) < 2 or len(location) > 200:
        raise HTTPException(
            status_code=400,
            detail="Invalid title or location."
        )

    if len(ward) > 100:
        raise HTTPException(
            status_code=400,
            detail="Ward name is too long."
        )

    # Extract GPS coordinates from the selected map location
    latitude = None
    longitude = None

    gps_match = re.search(
        r"GPS\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)",
        location,
        re.IGNORECASE
    )

    if gps_match:
        latitude = float(gps_match.group(1))
        longitude = float(gps_match.group(2))

        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise HTTPException(
                status_code=400,
                detail="Invalid GPS coordinates."
            )

    # Get ML prediction
    model_prediction = pipeline.predict([description])[0]

    confidence = None

    if hasattr(pipeline, "predict_proba"):
        confidence = float(
            max(pipeline.predict_proba([description])[0])
        )

    # Save selected category or ML prediction
    selected_category = category.strip()

    if selected_category:
        selected_category = CATEGORY_MAPPING.get(
            selected_category,
            selected_category
        )
    else:
        selected_category = model_prediction

    # Assign department
    selected_department = DEPARTMENT_MAPPING.get(
        selected_category,
        "General Administration Department"
    )

    # Parse incident date and time
    parsed_datetime = None

    if incident_datetime.strip():
        try:
            parsed_datetime = datetime.fromisoformat(
                incident_datetime.strip()
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid incident date and time."
            )

    # Save optional photograph
    photo_filename = None

    if photo and photo.filename:
        extension = ALLOWED_TYPES.get(photo.content_type)

        if not extension:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG and WEBP photos are allowed."
            )

        photo_data = await photo.read(MAX_PHOTO_SIZE + 1)

        if len(photo_data) > MAX_PHOTO_SIZE:
            raise HTTPException(
                status_code=400,
                detail="Photo size must not exceed 5 MB."
            )

        if not photo_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded photo is empty."
            )

        photo_filename = f"{uuid.uuid4().hex}{extension}"

        photo_path = UPLOAD_DIR / photo_filename
        photo_path.write_bytes(photo_data)

    # Create complaint record
    new_complaint = models.Complaint(
        user_id=user.id,
        title=title or "Untitled complaint",
        description=description,
        category=selected_category,
        predicted_category=model_prediction,
        prediction_confidence=confidence,
        location=location,
        ward=ward or None,
        latitude=latitude,
        longitude=longitude,
        incident_datetime=parsed_datetime,
        photo_filename=photo_filename,
        department=selected_department,
        status="Submitted"
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    # Create notification for the citizen
    new_notification = models.Notification(
        user_id=user.id,
        complaint_id=new_complaint.id,
        message=(
            f"Your complaint #{new_complaint.id} "
            "has been submitted successfully."
        ),
        is_read=0
    )

    db.add(new_notification)
    db.commit()

    # Return format expected by frontend
    return {
        "message": "Complaint submitted successfully.",
        "complaint": {
            "id": new_complaint.id,
            "title": new_complaint.title,
            "description": new_complaint.description,
            "category": new_complaint.category,
            "predicted_category": new_complaint.predicted_category,
            "prediction_confidence": new_complaint.prediction_confidence,
            "location": new_complaint.location,
            "ward": new_complaint.ward,
            "latitude": new_complaint.latitude,
            "longitude": new_complaint.longitude,
            "department": new_complaint.department,
            "status": new_complaint.status,
            "created_at": new_complaint.created_at
        }
    }


# 2. View complaints belonging to the logged-in citizen
@router.get("/")
def get_complaints(
    request: Request,
    search: str = "",
    category: str = "",
    status: str = "",
    db: Session = Depends(get_db)
):
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in as a citizen."
        )

    query = db.query(models.Complaint).filter(
        models.Complaint.user_id == user.id
    )

    # Search by title, description or location
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (models.Complaint.title.ilike(term)) |
            (models.Complaint.description.ilike(term)) |
            (models.Complaint.location.ilike(term))
        )

    # Filter by category
    if category.strip():
        selected_category = CATEGORY_MAPPING.get(
            category.strip(),
            category.strip()
        )
        query = query.filter(
            models.Complaint.category == selected_category
        )

    # Filter by status
    if status.strip():
        query = query.filter(
            models.Complaint.status == status.strip()
        )

    records = query.order_by(
        models.Complaint.created_at.desc()
    ).all()

    return {
        "complaints": [
            {
                "id": item.id,
                "title": item.title or "Untitled complaint",
                "description": item.description,
                "category": item.category,
                "location": item.location,
                "ward": item.ward,
                "latitude": item.latitude,
                "longitude": item.longitude,
                "status": item.status,
                "department": item.department,
                "photo": item.photo_filename,
                "created_at": item.created_at
            }
            for item in records
        ]
    }


# 3. Get all complaints for the community map
@router.get("/map")
def get_map_complaints(
    request: Request,
    db: Session = Depends(get_db)
):
    # Only logged-in citizens can view the community map
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in to view community complaints."
        )

    # Fetch complaints from all citizens
    records = db.query(models.Complaint).order_by(
        models.Complaint.created_at.desc()
    ).all()

    map_complaints = []

    for item in records:
        latitude = item.latitude
        longitude = item.longitude

        # Fallback for older complaints containing GPS in location text
        if latitude is None or longitude is None:
            if item.location:
                match = re.search(
                    r"GPS\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)",
                    item.location,
                    re.IGNORECASE
                )

                if match:
                    latitude = float(match.group(1))
                    longitude = float(match.group(2))

        # Ignore invalid coordinates
        if latitude is not None and longitude is not None:
            if not (
                -90 <= latitude <= 90
                and -180 <= longitude <= 180
            ):
                latitude = None
                longitude = None

        map_complaints.append({
            "id": item.id,
            "title": item.title or "Untitled complaint",
            "category": item.category,
            "location": item.location,
            "latitude": latitude,
            "longitude": longitude,
            "status": item.status
        })

    return {
        "complaints": map_complaints
    }


# 4. View a complaint by ID
@router.get("/{complaint_id}")
def get_complaint(
    complaint_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in as a citizen."
        )

    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == complaint_id,
        models.Complaint.user_id == user.id
    ).first()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found."
        )

    return {
        "complaint": {
            "id": complaint.id,
            "title": complaint.title or "Untitled complaint",
            "description": complaint.description,
            "category": complaint.category,
            "predicted_category": complaint.predicted_category,
            "prediction_confidence": complaint.prediction_confidence,
            "location": complaint.location,
            "ward": complaint.ward,
            "latitude": complaint.latitude,
            "longitude": complaint.longitude,
            "department": complaint.department,
            "status": complaint.status,
            "photo_filename": complaint.photo_filename,
            "created_at": complaint.created_at
        }
    }


# 5. Update complaint status
@router.patch("/{complaint_id}/status")
def update_complaint_status(
    complaint_id: int,
    update: schemas.ComplaintStatusUpdate,
    db: Session = Depends(get_db)
):
    allowed_statuses = [
        "Submitted",
        "Verified",
        "In Progress",
        "Resolved",
        "Rejected"
    ]

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint status"
        )

    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == complaint_id
    ).first()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    complaint.status = update.status

    db.commit()
    db.refresh(complaint)

    return {
        "message": "Complaint status updated successfully",
        "complaint": complaint
    }


# 6. Update complaint department
@router.patch("/{complaint_id}/department")
def update_complaint_department(
    complaint_id: int,
    update: schemas.ComplaintDepartmentUpdate,
    db: Session = Depends(get_db)
):
    allowed_departments = [
        "Road Maintenance Department",
        "Sanitation Department",
        "Electrical Department",
        "Water Supply Department",
        "Drainage Department",
        "General Administration Department"
    ]

    if update.department not in allowed_departments:
        raise HTTPException(
            status_code=400,
            detail="Invalid department"
        )

    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == complaint_id
    ).first()

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    complaint.department = update.department

    db.commit()
    db.refresh(complaint)

    return {
        "message": "Complaint department updated successfully",
        "complaint": complaint
    }


# 7. Filter complaints by status
@router.get("/filter/{status}")
def filter_complaints(
    status: str,
    db: Session = Depends(get_db)
):
    allowed_statuses = [
        "Submitted",
        "Verified",
        "In Progress",
        "Resolved",
        "Rejected"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid complaint status"
        )

    complaints = db.query(models.Complaint).filter(
        models.Complaint.status == status
    ).all()

    return complaints
