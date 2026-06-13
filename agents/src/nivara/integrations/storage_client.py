"""Supabase Storage client for media uploads (photos/videos)."""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Uploads files to a Supabase Storage bucket and returns public URLs."""

    def __init__(
        self,
        url: str | None = None,
        key: str | None = None,
        bucket: str | None = None,
    ) -> None:
        self.url = url or os.getenv("SUPABASE_URL", "")
        self.key = key or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.bucket = bucket or os.getenv("SUPABASE_STORAGE_BUCKET", "media")
        self._client: Any = None

    def is_configured(self) -> bool:
        return bool(self.url and self.key)

    def _get_client(self) -> Any:
        if self._client is None:
            from supabase import create_client

            self._client = create_client(self.url, self.key)
        return self._client

    def upload(
        self,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        folder: str = "uploads",
    ) -> dict[str, str]:
        if not self.is_configured():
            raise RuntimeError("Supabase Storage not configured — set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

        safe_name = f"{uuid.uuid4().hex[:12]}_{filename}"
        path = f"{folder.rstrip('/')}/{safe_name}"
        client = self._get_client()
        bucket = client.storage.from_(self.bucket)

        bucket.upload(
            path,
            content,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public_url = bucket.get_public_url(path)
        return {"path": path, "public_url": public_url, "filename": safe_name}

    def download(self, path: str) -> bytes | None:
        if not self.is_configured():
            return None
        try:
            data = self._get_client().storage.from_(self.bucket).download(path)
            return data
        except Exception as exc:
            logger.warning("Storage download failed for %s: %s", path, exc)
            return None
