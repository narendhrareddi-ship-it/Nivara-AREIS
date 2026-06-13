"""Google Gemini Veo API client for image-to-video generation."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "veo-3.1-generate-preview"


class VeoClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = BASE_URL,
        mock_mode: bool | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("VEO_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        env_mock = os.getenv("VEO_MOCK", "false").lower() == "true"
        self.mock_mode = env_mock if mock_mode is None else mock_mode
        self.model = os.getenv("VEO_MODEL", DEFAULT_MODEL)

    def is_configured(self) -> bool:
        return bool(self.api_key) or self.mock_mode

    def _headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def submit_image_to_video(
        self,
        image_content: bytes,
        prompt: str,
        mime_type: str = "image/jpeg",
        model: str | None = None,
    ) -> dict[str, Any]:
        model_id = model or self.model

        if self.mock_mode or not self.api_key:
            return {"name": "operations/mock-veo-job", "mock": True}

        image_b64 = base64.b64encode(image_content).decode("utf-8")
        payload = {
            "instances": [
                {
                    "prompt": prompt,
                    "image": {
                        "bytesBase64Encoded": image_b64,
                        "mimeType": mime_type,
                    },
                }
            ],
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/models/{model_id}:predictLongRunning",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def get_operation_status(self, operation_name: str) -> dict[str, Any]:
        if operation_name.startswith("operations/mock") or self.mock_mode:
            return {
                "done": True,
                "response": {
                    "generateVideoResponse": {
                        "generatedSamples": [
                            {"video": {"uri": "https://storage.mock.nivara.ai/videos/veo_mock.mp4"}}
                        ]
                    }
                },
                "mock": True,
            }

        path = operation_name if operation_name.startswith("operations/") else operation_name
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.base_url}/{path}",
                headers={"x-goog-api-key": self.api_key},
            )
            response.raise_for_status()
            return response.json()

    def _extract_video_uri(self, status_data: dict[str, Any]) -> str | None:
        try:
            return (
                status_data.get("response", {})
                .get("generateVideoResponse", {})
                .get("generatedSamples", [{}])[0]
                .get("video", {})
                .get("uri")
            )
        except (IndexError, AttributeError):
            return None

    async def generate_video(
        self,
        image_content: bytes,
        prompt: str,
        mime_type: str = "image/jpeg",
        poll_interval: float = 10.0,
        max_wait: float = 600.0,
    ) -> dict[str, Any]:
        submission = await self.submit_image_to_video(image_content, prompt, mime_type)
        operation_name = submission.get("name")
        if not operation_name:
            raise RuntimeError(f"Veo submission failed: {submission}")

        elapsed = 0.0
        while elapsed < max_wait:
            status_data = await self.get_operation_status(operation_name)

            if status_data.get("done"):
                video_uri = self._extract_video_uri(status_data)
                if status_data.get("error"):
                    raise RuntimeError(f"Veo generation failed: {status_data['error']}")
                return {
                    "operation_name": operation_name,
                    "status": "completed",
                    "video_url": video_uri,
                    "raw": status_data,
                    "mock": status_data.get("mock", False),
                }

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Veo job {operation_name} timed out after {max_wait}s")
