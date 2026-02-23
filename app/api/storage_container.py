from app.api.provider import Singleton
from app.domain.services.storage_service import StorageService
from app.infra.minio.storage_service import MinioStorageService

Storage = Singleton(StorageService, MinioStorageService())
