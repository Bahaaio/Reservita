from pathlib import Path

from app.services.storage import StorageService
from app.util.files import validate_image_file
from fastapi import HTTPException, UploadFile, status


class LocalStorageService(StorageService):
    def put(self, file: UploadFile, key: str) -> None:
        validate_image_file(file)

        # Create directory if it doesn't exist
        Path(key).parent.mkdir(parents=True, exist_ok=True)

        # Save file (overwrites if exists)
        try:
            with Path(key).open("wb") as f:
                f.write(file.file.read())
        except Exception:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to save file"
            )

    def get(self, key: str) -> bytes:
        try:
            return Path(key).read_bytes()
        except FileNotFoundError:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

    def delete(self, key: str) -> None:
        Path(key).unlink(missing_ok=True)
