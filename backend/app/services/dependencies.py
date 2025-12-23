from typing import Annotated

from fastapi import Depends
from app.services.local_storage import LocalStorageService
from app.services.s3 import S3Service
from app.services.storage import StorageService
from app.core.config import settings


def get_storage_service():
    if settings.s3_enabled:
        return S3Service()

    return LocalStorageService()


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
