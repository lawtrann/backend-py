import io
import logging
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.domain.exceptions import StorageError, StorageFileNotFoundError
from app.domain.services.storage_service import StorageObject, StorageService

logger = logging.getLogger(__name__)

minio_client = Minio(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


class MinioStorageService(StorageService):
    def __init__(self, client: Minio | None = None) -> None:
        self._client = client or minio_client

    def upload(self, bucket: str, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> StorageObject:
        try:
            stream = io.BytesIO(data)
            self._client.put_object(bucket, object_name, stream, length=len(data), content_type=content_type)
            return StorageObject(object_name=object_name, size=len(data), content_type=content_type)
        except S3Error as e:
            raise StorageError(f"Failed to upload '{object_name}': {e}") from e

    def download(self, bucket: str, object_name: str) -> bytes:
        response = None
        try:
            response = self._client.get_object(bucket, object_name)
            return response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise StorageFileNotFoundError(f"File '{object_name}' not found in bucket '{bucket}'") from e
            raise StorageError(f"Failed to download '{object_name}': {e}") from e
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def delete(self, bucket: str, object_name: str) -> None:
        try:
            self._client.remove_object(bucket, object_name)
        except S3Error as e:
            raise StorageError(f"Failed to delete '{object_name}': {e}") from e

    def exists(self, bucket: str, object_name: str) -> bool:
        try:
            self._client.stat_object(bucket, object_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise StorageError(f"Failed to check existence of '{object_name}': {e}") from e

    def presigned_url(self, bucket: str, object_name: str, expires_seconds: int | None = None) -> str:
        try:
            ttl = expires_seconds or settings.MINIO_PRESIGNED_URL_EXPIRY_SECONDS
            return self._client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=ttl))
        except S3Error as e:
            raise StorageError(f"Failed to generate presigned URL for '{object_name}': {e}") from e

    def ensure_bucket(self, bucket: str) -> None:
        try:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
        except S3Error as e:
            raise StorageError(f"Failed to ensure bucket '{bucket}': {e}") from e


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(
        "MinIO not ready, retrying in %s seconds (attempt %d/5)...",
        retry_state.next_action.sleep,
        retry_state.attempt_number,
    ),
)
def connect_to_storage() -> None:
    service = MinioStorageService()
    service.ensure_bucket(settings.MINIO_DEFAULT_BUCKET)
    logger.info("Storage connection established, bucket '%s' ready.", settings.MINIO_DEFAULT_BUCKET)
