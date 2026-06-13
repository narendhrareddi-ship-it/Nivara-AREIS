"""NIVARA CRM MCP Server — Supabase CRUD for leads and campaigns."""

from __future__ import annotations

import os
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="NIVARA CRM MCP", version="0.1.0")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def _get_crm() -> Any:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agents", "src"))
    from nivara.db.supabase_client import SupabaseCRM
    return SupabaseCRM(SUPABASE_URL, SUPABASE_KEY)


class CreateLeadRequest(BaseModel):
    full_name: str
    phone: str
    email: str | None = None
    source: str = "mcp"
    city: str = "Chennai"
    state: str = "Tamil Nadu"


class UpdateLeadRequest(BaseModel):
    lead_id: str
    status: str | None = None
    score: int | None = None
    ai_qualification_notes: str | None = None


class LogActivityRequest(BaseModel):
    lead_id: str | None = None
    activity_type: str
    title: str
    description: str | None = None
    agent_name: str = "crm-mcp"


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "server": "crm-mcp"}


@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    import json
    tools_path = os.path.join(os.path.dirname(__file__), "tools.json")
    with open(tools_path, encoding="utf-8") as f:
        return json.load(f)


@app.post("/call")
async def call_tool(request: ToolCallRequest) -> dict[str, Any]:
    crm = _get_crm()
    if not crm.is_configured():
        raise HTTPException(503, "Database not configured — check environment variables")
    args = request.arguments

    match request.name:
        case "list_leads":
            return {"result": crm.get_leads(status=args.get("status"), limit=args.get("limit", 50))}
        case "get_lead":
            lead = crm.get_lead(args["lead_id"])
            if not lead:
                raise HTTPException(404, "Lead not found")
            return {"result": lead}
        case "create_lead":
            return {"result": crm.create_lead(args)}
        case "update_lead":
            lead_id = args.pop("lead_id")
            return {"result": crm.update_lead(lead_id, args)}
        case "log_activity":
            return {"result": crm.log_activity(args)}
        case "list_campaigns":
            return {"result": crm.get_campaigns(status=args.get("status", "active"))}
        case _:
            raise HTTPException(400, f"Unknown tool: {request.name}")


if __name__ == "__main__":
    port = int(os.getenv("CRM_MCP_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
