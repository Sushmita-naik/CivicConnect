
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.routes.auth import get_logged_in_user

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_logged_in_user(request, db)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Please log in first."
        )

    query = db.query(models.Complaint).filter(
        models.Complaint.user_id == user.id
    )

    total = query.count()

    pending = query.filter(
        models.Complaint.status == "Submitted"
    ).count()

    under_review = query.filter(
        models.Complaint.status == "Verified"
    ).count()

    in_progress = query.filter(
        models.Complaint.status == "In Progress"
    ).count()

    resolved = query.filter(
        models.Complaint.status == "Resolved"
    ).count()

    recent_complaints = query.order_by(
        models.Complaint.created_at.desc()
    ).limit(5).all()

    recent = []

    for complaint in recent_complaints:
        recent.append({
            "id": complaint.id,
            "title": complaint.title or "Untitled complaint",
            "category": complaint.category or "Uncategorized",
            "status": complaint.status
        })

    return {
        "total": total,
        "pending": pending,
        "under_review": under_review,
        "in_progress": in_progress,
        "resolved": resolved,
        "recent": recent
    }
