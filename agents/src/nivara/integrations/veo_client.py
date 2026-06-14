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
    _quota_exhausted: set[str] = set()  # Track keys that hit 429 quota
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = BASE_URL,
        mock_mode: bool | None = None,
    ) -> None:
        # Support comma-separated keys for rotation
        raw_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("VEO_API_KEY", "")
        self.api_keys = [k.strip() for k in raw_key.split(",") if k.strip()]
        self.base_url = base_url.rstrip("/")
        env_mock = os.getenv("VEO_MOCK", "false").lower() == "true"
        self.mock_mode = env_mock if mock_mode is None else mock_mode
        self.model = os.getenv("VEO_MODEL", DEFAULT_MODEL)
        self._current_key_index = 0

    def is_configured(self) -> bool:
        return bool(self.api_keys) or self.mock_mode
    
    def _get_active_key(self) -> str | None:
        """Get next available key, skipping exhausted ones. Rotate if needed."""
        if not self.api_keys:
            return None
        
        # Try to find a non-exhausted key starting from current index
        for i in range(len(self.api_keys)):
            idx = (self._current_key_index + i) % len(self.api_keys)
            key = self.api_keys[idx]
            if key not in self._quota_exhausted:
                self._current_key_index = idx
                return key
        
        # All keys exhausted
        return None
    
    @property
    def api_key(self) -> str:
        """Get current active API key."""
        return self._get_active_key() or (self.api_keys[0] if self.api_keys else "")

    def _headers(self) -> dict[str, str]:
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    async def get_operation_status(self, operation_name: str) -> dict[str, Any]:
        self,
        image_content: bytes,
        prompt: str,
        mime_type: str = "image/jpeg",
        model: str | None = None,
    ) -> dict[str, Any]:
        model_id = model or self.model

        if self.mock_mode:
            logger.info("Veo mock mode enabled — returning mock operation")
            return {"name": "operations/mock-veo-job", "mock": True}
        
        active_key = self._get_active_key()
        if not active_key:
            logger.warning("Veo: all API keys exhausted or no keys configured — using mock")
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

        try:
            headers = {
                "x-goog-api-key": active_key,
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{model_id}:predictLongRunning",
                    headers=headers,
                    json=payload,
                )
                
                # Check for quota error
                if response.status_code == 429:
                    logger.warning(f"Veo key quota exhausted: {active_key[:20]}... — rotating to next key")
                    self._quota_exhausted.add(active_key)
                    # Recursive call to try next key
                    return await self.submit_image_to_video(image_content, prompt, mime_type, model)
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"Veo submission successful with key {active_key[:20]}...: {result.get('name')}")
                return result
        except Exception as e:
            logger.error(f"Veo submission failed ({e.__class__.__name__}): {e} — rotating key")
            self._quota_exhausted.add(active_key)
            
            # Try next key if available
            next_key = self._get_active_key()
            if next_key and next_key != active_key:
                logger.info(f"Retrying with next key...")
                return await self.submit_image_to_video(image_content, prompt, mime_type, model)
            
            logger.error("All Veo keys exhausted — using mock")
            return {"name": "operations/mock-veo-job", "mock": True}

    async def get_operation_status(self, operation_name: str) -> dict[str, Any]:
        if operation_name.startswith("operations/mock") or self.mock_mode:
            supabase_url = os.getenv("SUPABASE_URL", "https://mxjhwjxxqtkwsrwtqwuc.supabase.co").rstrip("/")
            mock_video_url = f"{supabase_url}/storage/v1/object/public/media/videos/mock_veo_output.mp4"
            return {
                "done": True,
                "response": {
                    "generateVideoResponse": {
                        "generatedSamples": [
                            {"video": {"uri": mock_video_url}}
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
