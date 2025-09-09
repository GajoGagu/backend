from pydantic import BaseModel
from typing import Optional


class PresignedUrlRequest(BaseModel):
    file_name: str
    file_type: str
    file_size: int


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_id: str
    expires_in: int = 3600


class UploadResponse(BaseModel):
    file_id: str
    url: str
    file_name: str
    file_size: int
    file_type: str
