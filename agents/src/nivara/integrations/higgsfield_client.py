"""Higgsfield Cloud API client for image-to-video generation."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://platform.higgsfield.ai"
DEFAULT_MODEL = "higgsfield-ai/dop/standard"


class HiggsfieldClient:
    def __init__(
        self,
        credentials: str | None = None,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = BASE_URL,
        mock_mode: bool | None = None,
    ) -> None:
        creds = credentials or os.getenv("HIGGSFIELD_CREDENTIALS", "")
        key = api_key or os.getenv("HIGGSFIELD_API_KEY", "")
        secret = api_secret or os.getenv("HIGGSFIELD_API_SECRET", "")

        if creds and ":" in creds:
            self._auth_header = f"Key {creds}"
        elif key and secret:
            self._auth_header = f"Key {key}:{secret}"
        else:
            self._auth_header = ""

        self.base_url = base_url.rstrip("/")
        env_mock = os.getenv("HIGGSFIELD_MOCK", "false").lower() == "true"
        self.mock_mode = env_mock if mock_mode is None else mock_mode
        self.model_id = os.getenv("HIGGSFIELD_VIDEO_MODEL", DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self._auth_header) or self.mock_mode

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._auth_header:
            headers["Authorization"] = self._auth_header
        return headers

    async def submit_image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5,
        model_id: str | None = None,
    ) -> dict[str, Any]:
        model = model_id or self.model_id

        if self.mock_mode or not self._auth_header:
            return {
                "status": "queued",
                "request_id": f"mock-{hash(image_url + prompt) % 10**8:08d}",
                "mock": True,
            }

        payload = {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/{model}",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def get_request_status(self, request_id: str) -> dict[str, Any]:
        if request_id.startswith("mock-") or self.mock_mode:
            return {
                "status": "completed",
                "request_id": request_id,
                "video": {"url": f"https://storage.mock.nivara.ai/videos/{request_id}.mp4"},
                "mock": True,
            }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/requests/{request_id}/status",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def generate_video(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5,
        poll_interval: float = 3.0,
        max_wait: float = 300.0,
    ) -> dict[str, Any]:
        submission = await self.submit_image_to_video(image_url, prompt, duration)
        request_id = submission.get("request_id")
        if not request_id:
            raise RuntimeError(f"Higgsfield submission failed: {submission}")

        elapsed = 0.0
        while elapsed < max_wait:
            status_data = await self.get_request_status(request_id)
            status = status_data.get("status", "")

            if status == "completed":
                video_url = None
                video = status_data.get("video")
                if isinstance(video, dict):
                    video_url = video.get("url")
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "video_url": video_url,
                    "raw": status_data,
                    "mock": status_data.get("mock", False),
                }

            if status in ("failed", "nsfw"):
                raise RuntimeError(f"Higgsfield generation {status}: {status_data}")

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Higgsfield job {request_id} timed out after {max_wait}s")
