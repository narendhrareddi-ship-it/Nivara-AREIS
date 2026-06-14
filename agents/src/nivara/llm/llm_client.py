"""LLM client — Gemini primary with Groq/OpenRouter cloud fallback."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from nivara.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMClient:
    """Cloud LLM client with automatic provider fallback on quota or API errors."""

    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout
        self._last_provider: str = "none"

    @property
    def last_provider(self) -> str:
        return self._last_provider

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        chain = self._provider_chain(settings.llm_provider.lower())

        for name in chain:
            try:
                text = await self._generate_with(name, prompt, system, temperature)
                if text:
                    self._last_provider = name
                    return text
            except Exception as exc:
                logger.warning("LLM provider %s failed: %s", name, exc)

        self._last_provider = "stub"
        return self._fallback_response(prompt)

    def _cloud_providers(self) -> list[str]:
        providers: list[str] = []
        if settings.gemini_api_key:
            providers.append("gemini")
        if settings.groq_api_key:
            providers.append("groq")
        if settings.openrouter_api_key:
            providers.append("openrouter")
        return providers

    def _provider_chain(self, provider: str) -> list[str]:
        cloud = self._cloud_providers()
        if not cloud:
            return []

        if provider in ("groq", "gemini", "openrouter"):
            # Primary provider first, then other configured backups
            return [provider] + [p for p in cloud if p != provider]

        # auto: gemini → groq → openrouter (whatever keys are set)
        return cloud

    async def _generate_with(
        self,
        provider: str,
        prompt: str,
        system: str | None,
        temperature: float,
    ) -> str:
        if provider == "groq":
            if not settings.groq_api_key:
                raise RuntimeError("GROQ_API_KEY not set")
            return await self._generate_openai_compatible(
                GROQ_API_URL,
                settings.groq_api_key,
                settings.groq_model,
                prompt,
                system,
                temperature,
            )
        if provider == "gemini":
            if not settings.gemini_api_key:
                raise RuntimeError("GEMINI_API_KEY not set")
            return await self._generate_gemini(prompt, system, temperature)
        if provider == "openrouter":
            if not settings.openrouter_api_key:
                raise RuntimeError("OPENROUTER_API_KEY not set")
            return await self._generate_openai_compatible(
                OPENROUTER_API_URL,
                settings.openrouter_api_key,
                settings.openrouter_model,
                prompt,
                system,
                temperature,
                extra_headers={"HTTP-Referer": "https://nivara-dashboard.onrender.com"},
            )
        raise RuntimeError(f"Unknown provider: {provider}")

    async def _generate_openai_compatible(
        self,
        url: str,
        api_key: str,
        model: str,
        prompt: str,
        system: str | None,
        temperature: float,
        extra_headers: dict[str, str] | None = None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])

    async def _generate_gemini(
        self,
        prompt: str,
        system: str | None,
        temperature: float,
    ) -> str:
        model = settings.gemini_llm_model
        url = f"{GEMINI_API_URL}/{model}:generateContent"
        params = {"key": settings.gemini_api_key}

        contents: list[dict[str, Any]] = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"System: {system}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(str(p.get("text", "")) for p in parts)

    def _fallback_response(self, prompt: str) -> str:
        return (
            "[LLM unavailable — all cloud providers failed or quota exceeded]\n"
            f"Processed prompt ({len(prompt)} chars). "
            "Set GEMINI_API_KEY plus GROQ_API_KEY or OPENROUTER_API_KEY for automatic fallback."
        )

    async def health_check(self) -> bool:
        return bool(self._cloud_providers())

    async def active_provider(self) -> str:
        chain = self._provider_chain(settings.llm_provider.lower())
        return chain[0] if chain else "stub"
