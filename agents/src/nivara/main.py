"""FastAPI server exposing the agent orchestrator."""

from __future__ import annotations

import logging
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

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
    ollama_ok = await orchestrator.llm.health_check()
    return {
        "status": "ok",
        "ollama": ollama_ok,
        "supabase_configured": orchestrator.crm.is_configured(),
    }


@app.post("/orchestrate", response_model=OrchestrateResponse)
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
        port=settings.orchestrator_port,
        reload=False,
    )


if __name__ == "__main__":
    run_server()
