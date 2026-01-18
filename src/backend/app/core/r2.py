"""
Cloudflare R2 Storage Client
S3-compatible object storage for course content

CONSTITUTIONAL COMPLIANCE:
- ✅ Content served verbatim (byte-for-byte)
- ❌ NO content transformation
- ❌ NO LLM processing of content
"""

from functools import lru_cache
from typing import Optional

import aioboto3
from botocore.config import Config

from app.config import get_settings

settings = get_settings()


class R2Client:
    """
    Async Cloudflare R2 client for content storage.

    All content is served verbatim without any transformation.
    """

    def __init__(self):
        """Initialize R2 client with credentials from settings."""
        self.session = aioboto3.Session()
        self.bucket_name = settings.r2_bucket_name
        self.endpoint_url = settings.r2_endpoint
        self.config = Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

    def _get_client_kwargs(self) -> dict:
        """Get common client configuration."""
        return {
            "service_name": "s3",
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": settings.r2_access_key,
            "aws_secret_access_key": settings.r2_secret_key,
            "config": self.config,
        }

    async def get_object(self, key: str) -> Optional[bytes]:
        """
        Get object content from R2.

        CONSTITUTIONAL COMPLIANCE:
        - ✅ Returns content verbatim (byte-for-byte)
        - ❌ NO transformation or processing

        Args:
            key: Object key in R2 (e.g., "chapters/ch1-intro-to-agents.md")

        Returns:
            Raw bytes content or None if not found
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=key)
                content = await response["Body"].read()
                return content
        except Exception as e:
            # Log error but return None for 404
            if "NoSuchKey" in str(e) or "404" in str(e):
                return None
            raise

    async def get_object_text(self, key: str, encoding: str = "utf-8") -> Optional[str]:
        """
        Get object content as text from R2.

        CONSTITUTIONAL COMPLIANCE:
        - ✅ Returns content verbatim (only decoding bytes to string)
        - ❌ NO content modification

        Args:
            key: Object key in R2
            encoding: Text encoding (default: utf-8)

        Returns:
            Text content or None if not found
        """
        content = await self.get_object(key)
        if content is None:
            return None
        return content.decode(encoding)

    async def put_object(
        self,
        key: str,
        body: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Put object content to R2.

        Args:
            key: Object key in R2
            body: Raw bytes content
            content_type: MIME content type
            metadata: Optional metadata dict

        Returns:
            True if successful
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                params = {
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "Body": body,
                }
                if content_type:
                    params["ContentType"] = content_type
                if metadata:
                    params["Metadata"] = metadata

                await s3.put_object(**params)
                return True
        except Exception:
            return False

    async def delete_object(self, key: str) -> bool:
        """
        Delete object from R2.

        Args:
            key: Object key in R2

        Returns:
            True if successful
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
                return True
        except Exception:
            return False

    async def object_exists(self, key: str) -> bool:
        """
        Check if object exists in R2.

        Args:
            key: Object key in R2

        Returns:
            True if object exists
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                await s3.head_object(Bucket=self.bucket_name, Key=key)
                return True
        except Exception:
            return False

    async def get_object_metadata(self, key: str) -> Optional[dict]:
        """
        Get object metadata from R2.

        Args:
            key: Object key in R2

        Returns:
            Metadata dict or None if not found
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                response = await s3.head_object(Bucket=self.bucket_name, Key=key)
                return {
                    "content_type": response.get("ContentType"),
                    "content_length": response.get("ContentLength"),
                    "last_modified": response.get("LastModified"),
                    "etag": response.get("ETag"),
                    "metadata": response.get("Metadata", {}),
                }
        except Exception:
            return None

    async def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[dict]:
        """
        List objects in R2 with given prefix.

        Args:
            prefix: Key prefix to filter (e.g., "chapters/")
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata dicts
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix,
                    MaxKeys=max_keys,
                )
                objects = []
                for obj in response.get("Contents", []):
                    objects.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj.get("ETag"),
                    })
                return objects
        except Exception:
            return []

    async def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> Optional[str]:
        """
        Generate a presigned URL for direct access.

        Args:
            key: Object key in R2
            expires_in: URL expiration in seconds (default: 1 hour)

        Returns:
            Presigned URL or None if failed
        """
        try:
            async with self.session.client(**self._get_client_kwargs()) as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expires_in,
                )
                return url
        except Exception:
            return None


# Singleton instance
_r2_client: Optional[R2Client] = None


@lru_cache
def get_r2_client() -> R2Client:
    """
    Get cached R2 client instance.

    Returns:
        Singleton R2Client instance
    """
    global _r2_client
    if _r2_client is None:
        _r2_client = R2Client()
    return _r2_client
