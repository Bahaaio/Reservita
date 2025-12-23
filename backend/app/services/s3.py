from io import BytesIO

import boto3
from app.core.config import settings
from app.services.storage import StorageService
from app.util.files import validate_image_file
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status


class S3Service(StorageService):
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )

    def put(self, file: UploadFile, key: str) -> None:
        validate_image_file(file)

        self.client.upload_fileobj(
            file.file,
            self.bucket,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

    def get(self, key: str) -> bytes:
        buf = BytesIO()
        try:
            self.client.download_fileobj(self.bucket, key, buf)
            return buf.getvalue()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
                raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found")

            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to retrieve file from storage",
            )

    def delete(self, key: str) -> None:
        self.client.delete_object(
            Bucket=self.bucket,
            Key=key,
        )
