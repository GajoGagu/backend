from pydantic import BaseModel
from typing import Optional


class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str = "info"
    is_read: bool = False
    created_at: str


class NotificationListResponse(BaseModel):
    notifications: list[Notification]
    total: int
    unread_count: int


class MarkAsReadRequest(BaseModel):
    notification_ids: list[str]
