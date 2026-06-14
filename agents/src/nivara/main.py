"""FastAPI server exposing the agent orchestrator."""

from __future__ import annotations

import logging
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from nivara.auth import verify_api_key
from nivara.config import settings
from nivara.orchestrator.graph import AgentOrchestrator
from nivara.regions import DEFAULT_REGION

logging.basicConfig(level=settings.agent_log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NIVARA REALTY Agent Orchestrator",
    description="LangGraph agent layer for digital marketing automation",
    version="0.1.0",
)

orchestrator = AgentOrchestrator()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": str(exc), "path": request.url.path})


class OrchestrateRequest(BaseModel):
    task: str = "daily_market_analysis"
    region: str = Field(default=DEFAULT_REGION)
    leads: list[dict[str, Any]] = Field(default_factory=list)
    agents: list[str] | None = None
    media_assets: list[dict[str, Any]] = Field(default_factory=list)
    project_id: str | None = None
    auto_publish_social: bool = True


class OrchestrateResponse(BaseModel):
    task: str
    region: str
    agent_outputs: dict[str, str]
    final_report: str | None = None


@app.get("/health")
async def health() -> dict[str, Any]:
    llm_ok = await orchestrator.llm.health_check()
    provider = await orchestrator.llm.active_provider()
    db_connected = False
    if orchestrator.crm.is_configured():
        try:
            orchestrator.crm._execute_query("SELECT 1 AS ok", fetch="one")
            db_connected = True
        except Exception as exc:
            logger.warning("DB health check failed: %s", exc)
    return {
        "status": "ok",
        "llm_available": llm_ok,
        "llm_provider": provider,
        "api_auth_enabled": bool(settings.orchestrator_api_key.strip()),
        "supabase_configured": orchestrator.crm.is_configured(),
        "db_connected": db_connected,
        "agent_count": len(orchestrator._agents),
        "pipeline_version": "20-agent",
    }


@app.post("/orchestrate", response_model=OrchestrateResponse, dependencies=[Depends(verify_api_key)])
async def orchestrate(request: OrchestrateRequest) -> OrchestrateResponse:
    logger.info("Orchestrating task=%s region=%s", request.task, request.region)
    result = await orchestrator.run(
        task=request.task,
        region=request.region,
        leads=request.leads,
        agents=request.agents,
        media_assets=request.media_assets,
        project_id=request.project_id,
        auto_publish_social=request.auto_publish_social,
    )
    return OrchestrateResponse(
        task=request.task,
        region=request.region,
        agent_outputs=result.get("agent_outputs", {}),
        final_report=result.get("final_report"),
    )


def run_server() -> None:
    uvicorn.run(
        "nivara.main:app",
        host=settings.orchestrator_host,
        port=settings.listen_port,
        reload=False,
    )


if __name__ == "__main__":
    run_server()
