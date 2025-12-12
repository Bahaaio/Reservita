import os
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings


def get_avatar_path(user_id: int) -> str:
    """Get the file path for a user's avatar"""
    return f"{settings.AVATAR_UPLOAD_DIR}/{user_id}.jpg"


def get_banner_path(banner_id: UUID) -> str:
    """Get the file path for an event banner"""
    return f"{settings.BANNER_UPLOAD_DIR}/{banner_id}.jpg"


def validate_image_file(file: UploadFile, max_size_mb: int = 5):
    """Validate that uploaded file is an image and within size limit"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start

    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file_size > max_size:
        raise HTTPException(400, f"File size exceeds maximum of {max_size_mb}MB")


def save_file(file: UploadFile, directory: str, filename: str):
    # Create directory if it doesn't exist
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    # Save file (overwrites if exists)
    file_path = dir_path / filename

    try:
        with file_path.open("wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(500, f"Failed to save file: {str(e)}")


def get_file_response(file_path: str, media_type: str = "image/jpeg") -> FileResponse:
    check_file_exists(file_path)
    return FileResponse(path=file_path, media_type=media_type)


def delete_file(file_path: str):
    path = Path(file_path)

    check_file_exists(file_path)
    path.unlink(missing_ok=True)


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
