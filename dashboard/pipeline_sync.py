"""Automatic 20-agent pipeline sync — keeps bot_logs at 20/20 without manual steps."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Callable

logger = logging.getLogger(__name__)

PIPELINE_AGENTS = [
    "MarketAnalyst", "RegulatoryWatch", "LocationScout", "CompetitorSpy", "CMO",
    "ContentStrategist", "Copywriter", "SEOAgent", "VisualDesigner", "SocialMediaManager",
    "PaidAdsManager", "LeadQualification", "SalesCoach", "WhatsAppAgent", "EmailMarketer",
    "AppointmentScheduler", "CRM", "Analytics", "COO", "CEO",
]

LEGACY_12_AGENTS = {
    "MarketAnalyst", "CompetitorSpy", "ContentStrategist", "SEOAgent", "VisualDesigner",
    "SocialMediaManager", "LeadQualification", "WhatsAppAgent", "AppointmentScheduler",
    "CRM", "Analytics", "CEO",
}


def latest_cycle_completed(query_fn: Callable) -> set[str]:
    """Agents that completed in the most recent pipeline cycle."""
    rows = query_fn(
        """
        SELECT agent_name, action
        FROM bot_logs
        WHERE timestamp >= COALESCE(
            (SELECT MAX(timestamp) FROM bot_logs
             WHERE agent_name = 'MarketAnalyst' AND action = 'Starting task'),
            NOW() - INTERVAL '1 hour'
        )
        ORDER BY timestamp ASC
        """,
    )
    done: set[str] = set()
    if not rows:
        return done
    for row in rows:
        if row.get("action") == "Task completed":
            done.add(row["agent_name"])
    return done


def needs_immediate_sync(query_fn: Callable) -> tuple[bool, str]:
    """Sync when pipeline is incomplete or legacy — not for staleness alone."""
    done = latest_cycle_completed(query_fn)
    expected = len(PIPELINE_AGENTS)
    if len(done) < expected:
        missing = [a for a in PIPELINE_AGENTS if a not in done]
        return True, f"{len(done)}/{expected} — missing {len(missing)} agents"
    if done == LEGACY_12_AGENTS:
        return True, "legacy 12-agent pipeline"
    if len(done) == 0:
        return True, "no pipeline logs"
    return False, f"{len(done)}/{expected} complete"


def needs_sync(
    query_fn: Callable,
    *,
    interval_minutes: int = 360,
    force_legacy: bool = True,
) -> tuple[bool, str]:
    """Return (should_sync, reason)."""
    done = latest_cycle_completed(query_fn)
    expected = len(PIPELINE_AGENTS)

    if len(done) < expected:
        missing = [a for a in PIPELINE_AGENTS if a not in done]
        return True, f"{len(done)}/{expected} agents — missing: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}"

    if force_legacy and done == LEGACY_12_AGENTS:
        return True, "legacy 12-agent pipeline detected"

    last = query_fn(
        "SELECT MAX(timestamp) AS t FROM bot_logs WHERE action = 'Task completed'",
        one=True,
    )
    if last and last.get("t"):
        ts = last["t"]
        if isinstance(ts, datetime):
            age = datetime.now(ts.tzinfo) - ts if ts.tzinfo else datetime.now() - ts
            if age > timedelta(minutes=interval_minutes):
                return True, f"pipeline stale ({int(age.total_seconds() // 60)} min old)"

    if len(done) == 0:
        return True, "no pipeline logs"

    return False, f"{len(done)}/{expected} agents up to date"


def bootstrap_agent_env(
    *,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    default_region: str = "Bangalore",
    groq_api_key: str = "",
    gemini_api_key: str = "",
    llm_provider: str = "auto",
) -> None:
    """Push dashboard DB/LLM settings into os.environ for the agents package."""
    env_map = {
        "DB_HOST": db_host,
        "DB_PORT": str(db_port),
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DEFAULT_REGION": default_region,
        "LLM_PROVIDER": llm_provider,
        "GROQ_API_KEY": groq_api_key,
        "GEMINI_API_KEY": gemini_api_key,
    }
    for key, value in env_map.items():
        if value:
            os.environ[key] = value


async def run_direct_pipeline(region: str = "Bangalore") -> dict[str, str]:
    """Run all 20 agents in-process (bypasses stale Render orchestrator)."""
    from nivara.orchestrator.graph import AgentOrchestrator, PIPELINE_ORDER

    orchestrator = AgentOrchestrator()
    result = await orchestrator.run(
        task="daily_market_analysis",
        region=region,
        agents=PIPELINE_ORDER,
    )
    return result.get("agent_outputs", {})


def run_direct_pipeline_sync(region: str = "Bangalore") -> dict[str, str]:
    return asyncio.run(run_direct_pipeline(region))


def run_http_pipeline(
    orch_url: str,
    region: str = "Bangalore",
    headers: dict[str, str] | None = None,
    timeout: int = 900,
) -> dict[str, str]:
    """Fallback: call remote orchestrator with explicit 20-agent list."""
    import requests

    response = requests.post(
        f"{orch_url.rstrip('/')}/orchestrate",
        json={
            "task": "daily_market_analysis",
            "region": region,
            "agents": PIPELINE_AGENTS,
        },
        headers=headers or {},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json().get("agent_outputs", {})


def auto_sync_pipeline(
    query_fn: Callable,
    *,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    default_region: str = "Bangalore",
    orch_url: str = "",
    orch_headers: dict[str, str] | None = None,
    interval_minutes: int = 360,
    prefer_direct: bool = True,
    groq_api_key: str = "",
    gemini_api_key: str = "",
) -> dict[str, str | int | bool]:
    """
    Sync pipeline if incomplete or stale.
    Returns status dict for dashboard display.
    """
    should, reason = needs_sync(query_fn, interval_minutes=interval_minutes)
    if not should:
        done = latest_cycle_completed(query_fn)
        return {
            "synced": False,
            "reason": reason,
            "agents_completed": len(done),
            "agents_expected": len(PIPELINE_AGENTS),
        }

    bootstrap_agent_env(
        db_host=db_host,
        db_port=db_port,
        db_name=db_name,
        db_user=db_user,
        db_password=db_password,
        default_region=default_region,
        groq_api_key=groq_api_key,
        gemini_api_key=gemini_api_key,
    )
    os.environ.setdefault("DB_SSLMODE", "require")

    outputs: dict[str, str] = {}
    mode = "none"
    error = ""

    if prefer_direct:
        try:
            outputs = run_direct_pipeline_sync(region=default_region)
            mode = "direct"
        except Exception as exc:
            logger.warning("Direct pipeline sync failed: %s", exc)
            error = str(exc)

    if len(outputs) < len(PIPELINE_AGENTS) and orch_url:
        try:
            outputs = run_http_pipeline(
                orch_url, region=default_region, headers=orch_headers
            )
            mode = "http"
            error = ""
        except Exception as exc:
            logger.warning("HTTP pipeline sync failed: %s", exc)
            if not error:
                error = str(exc)

    done = latest_cycle_completed(query_fn)
    return {
        "synced": len(outputs) >= len(PIPELINE_AGENTS) or len(done) >= len(PIPELINE_AGENTS),
        "reason": reason,
        "mode": mode,
        "agents_completed": max(len(outputs), len(done)),
        "agents_expected": len(PIPELINE_AGENTS),
        "error": error,
    }
