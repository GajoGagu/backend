from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.notification import Notification, NotificationListResponse, MarkAsReadRequest
from database.config import get_db
from database.service import DatabaseService
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications with pagination"""
    service = DatabaseService(db)
    
    notifications = service.get_user_notifications(
        user_id=current_user["id"],
        skip=skip,
        limit=limit
    )
    
    unread_count = service.get_unread_notification_count(current_user["id"])
    
    notification_list = [
        Notification(
            id=n.id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at.isoformat() if n.created_at else ""
        ) for n in notifications
    ]
    
    return NotificationListResponse(
        notifications=notification_list,
        total=len(notification_list),
        unread_count=unread_count
    )


@router.post("/mark-as-read")
def mark_notifications_as_read(
    request: MarkAsReadRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark specific notifications as read"""
    service = DatabaseService(db)
    
    updated_count = service.mark_notifications_as_read(
        user_id=current_user["id"],
        notification_ids=request.notification_ids
    )
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count
    }


@router.get("/unread-count")
def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    service = DatabaseService(db)
    
    unread_count = service.get_unread_notification_count(current_user["id"])
    
    return {
        "unread_count": unread_count
    }
