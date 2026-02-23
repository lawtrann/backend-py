from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class StorageObject:
    object_name: str
    size: int
    content_type: str


class StorageService(ABC):
    @abstractmethod
    def upload(self, bucket: str, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> StorageObject: ...

    @abstractmethod
    def download(self, bucket: str, object_name: str) -> bytes: ...

    @abstractmethod
    def delete(self, bucket: str, object_name: str) -> None: ...

    @abstractmethod
    def exists(self, bucket: str, object_name: str) -> bool: ...

    @abstractmethod
    def presigned_url(self, bucket: str, object_name: str, expires_seconds: int | None = None) -> str: ...

    @abstractmethod
    def ensure_bucket(self, bucket: str) -> None: ...
