"""PixVerse API client for image-to-video generation."""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://app-api.pixverse.ai"


class PixverseClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = BASE_URL,
        mock_mode: bool | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("PIXVERSE_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        env_mock = os.getenv("PIXVERSE_MOCK", "false").lower() == "true"
        self.mock_mode = env_mock if mock_mode is None else mock_mode
        self.model = os.getenv("PIXVERSE_MODEL", "v5.5")
        self.quality = os.getenv("PIXVERSE_QUALITY", "720p")

    def is_configured(self) -> bool:
        return bool(self.api_key) or self.mock_mode

    def _headers(self) -> dict[str, str]:
        return {
            "API-KEY": self.api_key,
            "Ai-trace-id": str(uuid.uuid4()),
        }

    def _check_response(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("ErrCode", 0) != 0:
            raise RuntimeError(f"PixVerse API error {data.get('ErrCode')}: {data.get('ErrMsg')}")
        return data.get("Resp", {})

    async def upload_image_bytes(
        self,
        content: bytes,
        filename: str = "image.jpg",
        mime_type: str = "image/jpeg",
    ) -> dict[str, Any]:
        if self.mock_mode or not self.api_key:
            return {"img_id": 99999, "img_url": f"https://mock.pixverse.ai/{filename}", "mock": True}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/openapi/v2/image/upload",
                headers=self._headers(),
                files={"image": (filename, content, mime_type)},
            )
            response.raise_for_status()
            return self._check_response(response.json())

    async def upload_image_url(self, image_url: str) -> dict[str, Any]:
        if self.mock_mode or not self.api_key:
            return {"img_id": 99999, "img_url": image_url, "mock": True}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/openapi/v2/image/upload",
                headers={**self._headers(), "Content-Type": "application/json"},
                data={"image_url": image_url},
            )
            response.raise_for_status()
            return self._check_response(response.json())

    async def submit_image_to_video(
        self,
        img_id: int,
        prompt: str,
        duration: int = 5,
        model: str | None = None,
        quality: str | None = None,
    ) -> dict[str, Any]:
        if self.mock_mode or not self.api_key:
            return {"video_id": 88888, "mock": True}

        payload = {
            "img_id": img_id,
            "prompt": prompt,
            "duration": duration,
            "model": model or self.model,
            "quality": quality or self.quality,
            "motion_mode": "normal",
            "water_mark": False,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/openapi/v2/video/img/generate",
                headers={**self._headers(), "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return self._check_response(response.json())

    async def get_video_status(self, video_id: int) -> dict[str, Any]:
        if self.mock_mode or not self.api_key:
            return {
                "status": 1,
                "url": f"https://storage.mock.nivara.ai/videos/{video_id}.mp4",
                "mock": True,
            }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/openapi/v2/video/result/{video_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return self._check_response(response.json())

    async def generate_video(
        self,
        image_content: bytes | None = None,
        image_url: str | None = None,
        filename: str = "image.jpg",
        mime_type: str = "image/jpeg",
        prompt: str = "Cinematic camera movement",
        duration: int = 5,
        poll_interval: float = 5.0,
        max_wait: float = 300.0,
    ) -> dict[str, Any]:
        if image_content:
            upload = await self.upload_image_bytes(image_content, filename, mime_type)
        elif image_url:
            upload = await self.upload_image_url(image_url)
        else:
            raise ValueError("image_content or image_url required")

        img_id = upload.get("img_id")
        if not img_id:
            raise RuntimeError(f"PixVerse upload failed: {upload}")

        submission = await self.submit_image_to_video(img_id, prompt, duration)
        video_id = submission.get("video_id")
        if not video_id:
            raise RuntimeError(f"PixVerse submission failed: {submission}")

        elapsed = 0.0
        while elapsed < max_wait:
            status_data = await self.get_video_status(video_id)
            status = status_data.get("status")

            if status == 1:
                return {
                    "video_id": video_id,
                    "img_id": img_id,
                    "status": "completed",
                    "video_url": status_data.get("url"),
                    "raw": status_data,
                    "mock": status_data.get("mock", False),
                }

            if status in (6, 7, 8):
                raise RuntimeError(f"PixVerse generation failed (status={status}): {status_data}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"PixVerse job {video_id} timed out after {max_wait}s")
