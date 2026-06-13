"""LLM client — Ollama locally, cloud fallback (Groq/Gemini/OpenRouter) in production."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from nivara.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OllamaClient:
    """Unified LLM client with Ollama-first and cloud fallback chain."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
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
        provider = settings.llm_provider.lower()
        chain = self._provider_chain(provider)

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

    def _provider_chain(self, provider: str) -> list[str]:
        if provider == "ollama":
            return ["ollama"]
        if provider == "groq":
            return ["groq"]
        if provider == "gemini":
            return ["gemini"]
        if provider == "openrouter":
            return ["openrouter"]

        # auto: local first, then any configured cloud provider
        chain = ["ollama"]
        if settings.groq_api_key:
            chain.append("groq")
        if settings.gemini_api_key:
            chain.append("gemini")
        if settings.openrouter_api_key:
            chain.append("openrouter")
        return chain

    async def _generate_with(
        self,
        provider: str,
        prompt: str,
        system: str | None,
        temperature: float,
    ) -> str:
        if provider == "ollama":
            if not await self._ollama_available():
                raise RuntimeError("Ollama offline")
            return await self._generate_ollama(prompt, system, temperature)
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
                extra_headers={"HTTP-Referer": "https://nivara-areis.streamlit.app"},
            )
        raise RuntimeError(f"Unknown provider: {provider}")

    async def _ollama_available(self) -> bool:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except httpx.HTTPError:
                return False

    async def _generate_ollama(
        self,
        prompt: str,
        system: str | None,
        temperature: float,
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
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("message", {}).get("content", ""))

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
            "[LLM unavailable — no Ollama or cloud API configured]\n"
            f"Processed prompt ({len(prompt)} chars). "
            "Set GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY for production."
        )

    async def health_check(self) -> bool:
        if await self._ollama_available():
            return True
        if settings.groq_api_key or settings.gemini_api_key or settings.openrouter_api_key:
            return True
        return False

    async def active_provider(self) -> str:
        chain = self._provider_chain(settings.llm_provider.lower())
        for name in chain:
            if name == "ollama" and await self._ollama_available():
                return "ollama"
            if name == "groq" and settings.groq_api_key:
                return "groq"
            if name == "gemini" and settings.gemini_api_key:
                return "gemini"
            if name == "openrouter" and settings.openrouter_api_key:
                return "openrouter"
        return "stub"
