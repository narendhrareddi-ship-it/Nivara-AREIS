"""NIVARA Social MCP Server — mock FB/IG/LinkedIn/X/YouTube integrations."""

from __future__ import annotations

import json
import logging
import os
import uuid
import sys
from datetime import UTC, datetime
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI(title="NIVARA Social MCP", version="0.1.0")

# Add agents source to path to use the common CRM client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "src"))
from nivara.db.supabase_client import SupabaseCRM

def _get_crm() -> SupabaseCRM:
    return SupabaseCRM()

class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def _store_post(data: dict[str, Any]) -> dict[str, Any]:
    try:
        crm = _get_crm()
        if crm.is_configured():
            return crm.create_social_post(data)
    except Exception as e:
        logger.error("Failed to store social post in CRM: %s", e)
    
    return {**data, "stored": False, "error": "CRM not configured or error occurred"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "server": "social-mcp", "mode": "mock"}


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    with open(os.path.join(os.path.dirname(__file__), "tools.json"), encoding="utf-8") as f:
        return json.load(f)


@app.post("/webhook/{platform}")
async def platform_webhook(platform: str, payload: dict[str, Any]) -> dict[str, Any]:
    logger.info("Social webhook [%s]: %s", platform, payload)
    return {
        "received": True,
        "platform": platform,
        "event": payload,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    args = request.arguments

    match request.name:
        case "publish_post":
            post_id = str(uuid.uuid4())
            media_urls = args.get("media_urls", [])
            media_type = args.get("media_type", "text")
            record = {
                "platform": args["platform"],
                "content": args["content"],
                "campaign_id": args.get("campaign_id"),
                "project_id": args.get("project_id"),
                "media_urls": media_urls,
                "published_at": datetime.now(UTC).isoformat(),
                "external_post_id": f"mock_{post_id[:8]}",
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "reach": 0,
                "is_mock": True,
                "post_status": "published",
                "media_asset_id": args.get("media_asset_id"),
                "metadata": {
                    "phase": 2,
                    "mock": True,
                    "media_type": media_type,
                    "media_urls": media_urls,
                },
            }
            stored = _store_post(record)
            logger.info("Mock published to %s: %s", args["platform"], args["content"][:80])
            return {"result": stored}
        case "schedule_post":
            record = {
                "platform": args["platform"],
                "content": args["content"],
                "scheduled_at": args["scheduled_at"],
                "is_mock": True,
                "metadata": {"scheduled": True},
            }
            return {"result": _store_post(record)}
        case "get_engagement":
            return {
                "result": {
                    "post_id": args["post_id"],
                    "likes": 42,
                    "shares": 7,
                    "comments": 3,
                    "reach": 1200,
                    "is_mock": True,
                }
            }
        case "webhook_receiver":
            return {
                "result": {
                    "platform": args["platform"],
                    "event_type": args["event_type"],
                    "payload": args.get("payload", {}),
                    "processed_at": datetime.now(UTC).isoformat(),
                }
            }
        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("SOCIAL_MCP_PORT", "8003")))
    uvicorn.run(app, host="0.0.0.0", port=port)
