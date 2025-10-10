import uuid
import os
import boto3
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from models.upload import PresignedUrlRequest, PresignedUrlResponse
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PRESIGNED_EXPIRES = int(os.getenv("PRESIGNED_EXPIRES", "900"))  # seconds
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "ap-northeast-2")
S3_PUBLIC_BASE_URL = os.getenv("S3_PUBLIC_BASE_URL", f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com")


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def is_allowed_file(filename: str) -> bool:
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def build_object_key(user_id: str, file_name: str) -> str:
    ext = get_file_extension(file_name)
    return f"uploads/{user_id}/{uuid.uuid4()}{ext}"


@router.post("/presigned-url", response_model=PresignedUrlResponse)
def get_presigned_url(
    request: PresignedUrlRequest,
    current_user: dict = Depends(get_current_user)
):
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 configuration missing")

    if not is_allowed_file(request.file_name):
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed types: {allowed}")

    if request.file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")

    object_key = build_object_key(current_user["id"], request.file_name)

    s3 = boto3.client("s3", region_name=S3_REGION)
    try:
        presigned = s3.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=object_key,
            Fields={"Content-Type": request.file_type},
            Conditions=[["content-length-range", 0, MAX_FILE_SIZE], {"Content-Type": request.file_type}],
            ExpiresIn=PRESIGNED_EXPIRES,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {e}")

    # For clients we return the S3 form target URL; file_id can be the object key
    upload_url = presigned.get("url")
    file_id = object_key
    return PresignedUrlResponse(upload_url=upload_url, file_id=file_id, expires_in=PRESIGNED_EXPIRES)
