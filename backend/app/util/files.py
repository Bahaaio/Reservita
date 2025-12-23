from io import BytesIO
from uuid import UUID

from app.core.config import settings
from fastapi import HTTPException, UploadFile
from fastapi.responses import StreamingResponse


def get_avatar_key(user_id: int) -> str:
    """Get the file path for a user's avatar"""
    return f"{settings.AVATAR_UPLOAD_DIR}/{user_id}.jpg"


def get_banner_key(banner_id: UUID) -> str:
    """Get the file path for an event banner"""
    return f"{settings.BANNER_UPLOAD_DIR}/{banner_id}.jpg"


def validate_image_file(file: UploadFile, max_size_mb: int = 5):
    """Validate that uploaded file is an image and within size limit"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/jpeg"):
        raise HTTPException(400, "File must be a jpeg image")

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start

    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file_size > max_size:
        raise HTTPException(400, f"File size exceeds maximum of {max_size_mb}MB")


def to_image_response(file: bytes) -> StreamingResponse:
    return StreamingResponse(BytesIO(file), media_type="image/jpeg")
