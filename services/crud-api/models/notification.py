from pydantic import BaseModel


class Notification(BaseModel):
    id: str
    category: str
    title: str
    body: str
    read: bool = False
    created_at: str
