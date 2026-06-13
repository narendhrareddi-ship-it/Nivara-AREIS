"""Ollama LLM client (free, local inference)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from nivara.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                return str(data.get("message", {}).get("content", ""))
            except httpx.HTTPError as exc:
                logger.warning("Ollama unavailable, using fallback: %s", exc)
                return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        return (
            f"[Ollama offline — stub response for Phase 1]\n"
            f"Processed prompt ({len(prompt)} chars). "
            f"Start Ollama and pull model: ollama pull {self.model}"
        )

    async def health_check(self) -> bool:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except httpx.HTTPError:
                return False
