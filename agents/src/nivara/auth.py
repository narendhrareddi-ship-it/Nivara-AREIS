"""Optional API key authentication for orchestrator endpoints."""

from __future__ import annotations

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from nivara.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Require X-API-Key header when ORCHESTRATOR_API_KEY is configured."""
    configured = settings.orchestrator_api_key.strip()
    if not configured:
        return
    if not api_key or api_key != configured:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
