"""
Predictify — Storage Service (T3.4)
Abstraction layer for file storage with two backends:
  - local: Filesystem storage for development
  - s3: AWS S3 (or S3-compatible) for production

Usage:
    from app.services.storage_service import storage_service

    # Upload
    key = await storage_service.upload(file_data, filename, mime_type)

    # Download
    data = await storage_service.download(key)

    # Delete
    await storage_service.delete(key)
"""
import asyncio
import hashlib
import re
from pathlib import Path
from typing import Optional
from uuid import uuid4

import structlog

from app.core.config import settings

logger = structlog.get_logger()


def validate_storage_key(key: str) -> None:
    """Accept only portable relative object paths, including legacy safe keys."""
    if (not isinstance(key, str) or not key or "\\" in key or ":" in key
            or any(ord(char) < 32 for char in key)
            or any(part in ("", ".", "..") or part.endswith((".", " "))
                   for part in key.split("/"))):
        raise ValueError("Invalid storage key")


class StorageBackend:
    """Base class for storage backends."""

    async def upload(self, data: bytes, key: str, mime_type: str = "") -> str:
        raise NotImplementedError

    async def download(self, key: str) -> Optional[bytes]:
        raise NotImplementedError

    async def delete(self, key: str) -> bool:
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """Filesystem-based storage for local development."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("storage_backend_init", backend="local", path=str(self.base_path))

    def _resolve_key(self, key: str) -> Path:
        validate_storage_key(key)
        path = (self.base_path / key).resolve()
        if not path.is_relative_to(self.base_path) or path == self.base_path:
            raise ValueError("Invalid storage key")
        return path

    async def upload(self, data: bytes, key: str, mime_type: str = "") -> str:
        """Write file to local filesystem."""
        file_path = self._resolve_key(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Run blocking I/O in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write_file, file_path, data)

        logger.debug("storage_uploaded", backend="local", key=key, size=len(data))
        return key

    async def download(self, key: str) -> Optional[bytes]:
        """Read file from local filesystem."""
        file_path = self._resolve_key(key)
        if not file_path.exists():
            return None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._read_file, file_path)

    async def delete(self, key: str) -> bool:
        """Delete file from local filesystem."""
        file_path = self._resolve_key(key)
        if file_path.exists():
            file_path.unlink()
            logger.debug("storage_deleted", backend="local", key=key)
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if file exists in local filesystem."""
        return self._resolve_key(key).is_file()

    @staticmethod
    def _write_file(path: Path, data: bytes):
        path.write_bytes(data)

    @staticmethod
    def _read_file(path: Path) -> bytes:
        with path.open("rb") as stream:
            return stream.read(10 * 1024 * 1024 + 1)


class S3StorageBackend(StorageBackend):
    """AWS S3 (or S3-compatible) storage for production."""

    def __init__(
        self,
        bucket: str,
        region: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str = "",
    ):
        import boto3

        self.bucket = bucket
        client_kwargs = {
            "service_name": "s3",
            "region_name": region,
        }
        if access_key and secret_key:
            client_kwargs.update(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url

        self.client = boto3.client(**client_kwargs)
        logger.info(
            "storage_backend_init",
            backend="s3",
            bucket=bucket,
            region=region,
            endpoint=endpoint_url or "aws-default",
        )

    async def upload(self, data: bytes, key: str, mime_type: str = "") -> str:
        """Upload file to S3."""
        loop = asyncio.get_event_loop()
        extra_args = {}
        if mime_type:
            extra_args["ContentType"] = mime_type

        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                **extra_args,
            ),
        )
        logger.debug("storage_uploaded", backend="s3", key=key, size=len(data))
        return key

    async def download(self, key: str) -> Optional[bytes]:
        """Download file from S3."""
        loop = asyncio.get_event_loop()
        def read_object():
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            body = response["Body"]
            try:
                return body.read(10 * 1024 * 1024 + 1)
            finally:
                body.close()
        try:
            return await loop.run_in_executor(None, read_object)
        except self.client.exceptions.NoSuchKey:
            return None

    async def delete(self, key: str) -> bool:
        """Delete file from S3."""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_object(Bucket=self.bucket, Key=key),
            )
            logger.debug("storage_deleted", backend="s3", key=key)
            return True
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.head_object(Bucket=self.bucket, Key=key),
            )
            return True
        except Exception:
            return False


class StorageService:
    """Facade that auto-selects backend based on STORAGE_BACKEND config."""

    def __init__(self):
        self._backend: Optional[StorageBackend] = None

    @property
    def backend(self) -> StorageBackend:
        """Lazy-init the backend on first use."""
        if self._backend is None:
            if settings.STORAGE_BACKEND == "s3":
                self._backend = S3StorageBackend(
                    bucket=settings.S3_BUCKET_NAME,
                    region=settings.S3_REGION,
                    access_key=settings.S3_ACCESS_KEY_ID,
                    secret_key=settings.S3_SECRET_ACCESS_KEY,
                    endpoint_url=settings.S3_ENDPOINT_URL,
                )
            else:
                self._backend = LocalStorageBackend(settings.LOCAL_STORAGE_PATH)
        return self._backend

    def generate_key(self, user_id: str, filename: str) -> str:
        """Generate a unique storage key for a file.

        Client-controlled names never become path components.
        """
        namespace = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
        return f"documents/{namespace}/{uuid4().hex}"

    def belongs_to_user(self, key: str, user_id: str) -> bool:
        validate_storage_key(key)
        namespace = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
        return key.startswith(f"documents/{namespace}/") or (
            re.fullmatch(r"[A-Za-z0-9_-]+", user_id) is not None
            and key.startswith(f"documents/{user_id}/")
        )

    async def upload(self, data: bytes, key: str, mime_type: str = "") -> str:
        validate_storage_key(key)
        return await self.backend.upload(data, key, mime_type)

    async def download(self, key: str) -> Optional[bytes]:
        validate_storage_key(key)
        return await self.backend.download(key)

    async def delete(self, key: str) -> bool:
        validate_storage_key(key)
        return await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        validate_storage_key(key)
        return await self.backend.exists(key)


# Module-level singleton
storage_service = StorageService()
