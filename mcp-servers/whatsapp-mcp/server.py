"""NIVARA WhatsApp MCP Server — mock webhook + lead scoring.
Real WhatsApp Business API requires Meta Business verification and is paid
beyond free tier limits. Phase 1 uses mock webhooks only.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()
logger = logging.getLogger(__name__)
app = FastAPI(title="NIVARA WhatsApp MCP", version="0.1.0")

# Add agents source to path to use the common CRM client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "src"))
from nivara.db.supabase_client import SupabaseCRM

def _get_crm() -> SupabaseCRM:
    return SupabaseCRM()

_conversations: dict[str, list[dict[str, Any]]] = {}


class WebhookMessage(BaseModel):
    phone: str
    message: str
    lead_id: str | None = None
    sender_name: str | None = None


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def score_conversation(messages: list[str]) -> tuple[int, str]:
    text = " ".join(messages).lower()
    score = 20

    if re.search(r"\b(budget|price|cost|₹|lakh|crore)\b", text):
        score += 25
    if re.search(r"\b(visit|site|show|flat|villa|plot|bhk)\b", text):
        score += 20
    if re.search(r"\b(omr|ecr|amaravati|vizag|chennai|andhra)\b", text):
        score += 15
    if re.search(r"\b(urgent|immediate|this month|ready)\b", text):
        score += 15
    if re.search(r"\b(just looking|maybe later|not sure)\b", text):
        score -= 20

    score = max(0, min(100, score))
    if score >= 70:
        tier = "hot"
    elif score >= 40:
        tier = "warm"
    else:
        tier = "cold"
    return score, tier


def _log_to_crm(phone: str, message: str, score: int, lead_id: str | None) -> None:
    try:
        crm = _get_crm()
        if crm.is_configured():
            crm.log_activity({
                "lead_id": lead_id,
                "activity_type": "whatsapp",
                "title": f"WhatsApp message from {phone}",
                "description": message[:500],
                "performed_by": "whatsapp-mcp",
                "agent_name": "LeadQualification",
                "metadata": {"score": score, "mock": True},
            })
    except Exception as e:
        logger.error("Failed to log WhatsApp activity to CRM: %s", e)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "server": "whatsapp-mcp", "mode": "mock"}


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    with open(os.path.join(os.path.dirname(__file__), "tools.json"), encoding="utf-8") as f:
        return json.load(f)


@app.post("/webhook/message")
async def webhook_message(body: WebhookMessage) -> dict[str, Any]:
    phone = body.phone
    if phone not in _conversations:
        _conversations[phone] = []

    _conversations[phone].append({
        "role": "user",
        "content": body.message,
        "at": datetime.now(UTC).isoformat(),
    })

    messages = [m["content"] for m in _conversations[phone]]
    score, tier = score_conversation(messages)
    _log_to_crm(phone, body.message, score, body.lead_id)

    reply = (
        f"Thank you for your interest in NIVARA REALTY! "
        f"We have premium projects in Chennai and Andhra Pradesh. "
        f"Would you like to schedule a site visit?"
    )
    _conversations[phone].append({"role": "bot", "content": reply, "at": datetime.now(UTC).isoformat()})

    logger.info("WhatsApp mock [%s] score=%d tier=%s", phone, score, tier)
    return {
        "phone": phone,
        "score": score,
        "tier": tier,
        "reply": reply,
        "mock": True,
        "note": "Real WhatsApp Business API requires Meta verification (paid in production)",
    }


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    args = request.arguments

    match request.name:
        case "handle_message":
            result = await webhook_message(WebhookMessage(**args))
            return {"result": result}
        case "send_message":
            phone = args["phone"]
            message = args["message"]
            logger.info("Mock WhatsApp send to %s: %s", phone, message[:80])
            return {"result": {"sent": True, "mock": True, "phone": phone, "message": message}}
        case "score_lead":
            conv = args.get("conversation") or [
                m["content"] for m in _conversations.get(args["phone"], [])
            ]
            score, tier = score_conversation(conv)
            return {"result": {"phone": args["phone"], "score": score, "tier": tier}}
        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("WHATSAPP_MCP_PORT", "8004"))
    uvicorn.run(app, host="0.0.0.0", port=port)
