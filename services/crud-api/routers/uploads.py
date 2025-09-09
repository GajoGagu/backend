import uuid
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.upload import PresignedUrlRequest, PresignedUrlResponse, UploadResponse
from database.config import get_db
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

# Simple file storage configuration (in production, use cloud storage like S3)
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def ensure_upload_dir():
    """Ensure upload directory exists"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(
    request: PresignedUrlRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate presigned URL for file upload (simplified implementation)"""
    
    # Validate file type
    if not is_allowed_file(request.file_name):
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    if request.file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # In a real implementation, this would generate a presigned URL for cloud storage
    # For now, we'll return a mock presigned URL
    upload_url = f"/uploads/{file_id}"
    
    return PresignedUrlResponse(
        upload_url=upload_url,
        file_id=file_id,
        expires_in=3600
    )


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload file directly"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = get_file_extension(file.filename)
    new_filename = f"{file_id}{file_extension}"
    
    # Ensure upload directory exists
    ensure_upload_dir()
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Generate file URL (in production, this would be a cloud storage URL)
    file_url = f"/uploads/{new_filename}"
    
    return UploadResponse(
        file_id=file_id,
        url=file_url,
        file_name=file.filename,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream"
    )


@router.get("/{file_id}")
def get_file(file_id: str):
    """Get uploaded file (simplified implementation)"""
    # In production, this would serve files from cloud storage
    # For now, return a placeholder response
    return JSONResponse(
        content={
            "message": "File access endpoint",
            "file_id": file_id,
            "note": "In production, this would serve the actual file"
        }
    )
