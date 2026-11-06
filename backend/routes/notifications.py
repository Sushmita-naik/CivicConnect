from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Notification
from backend.routes.auth import get_logged_in_user

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


def get_citizen(request, db):
    user = get_logged_in_user(request, db)

    if not user or user.role != "citizen":
        raise HTTPException(
            status_code=401,
            detail="Please log in as a citizen."
        )

    return user


# Get notifications
@router.get("")
def get_notifications(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_citizen(request, db)

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return {
        "notifications": [
            {
                "id": n.id,
                "complaint_id": n.complaint_id,
                "message": n.message,
                "is_read": bool(n.is_read),
                "created_at": n.created_at
            }
            for n in notifications
        ]
    }


# Mark all notifications as read
@router.post("/read")
def mark_notifications_read(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_citizen(request, db)

    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == 0
    ).update({"is_read": 1})

    db.commit()

    return {
        "message": "All notifications marked as read."
    }