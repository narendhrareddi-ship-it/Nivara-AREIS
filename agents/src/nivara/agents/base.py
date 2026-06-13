"""Base agent types and shared state."""

from __future__ import annotations

import logging
from typing import Annotated, Any, TypedDict

logger = logging.getLogger(__name__)

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list[Any], add_messages]
    task: str
    region: str
    leads: list[dict[str, Any]]
    campaigns: list[dict[str, Any]]
    competitors: list[dict[str, Any]]
    analytics: list[dict[str, Any]]
    agent_outputs: dict[str, str]
    next_agent: str
    media_videos: list[dict[str, Any]]
    media_assets: list[dict[str, Any]]
    project_id: str
    auto_publish_social: bool


from nivara.regions import DEFAULT_REGION, market_scope


class BaseAgent:
    name: str = "BaseAgent"
    role: str = "Base agent"

    def __init__(self, llm: Any, crm: Any) -> None:
        self.llm = llm
        self.crm = crm

    def system_prompt(self, region: str = DEFAULT_REGION) -> str:
        return (
            f"You are the {self.name} agent for NIVARA REALTY, a digital marketing agency "
            f"specializing in real estate in {market_scope(region)}. "
            f"Role: {self.role}. Provide concise, actionable insights focused on Bangalore."
        )

    async def run(self, state: AgentState) -> dict[str, Any]:
        raise NotImplementedError

    def log_action(self, action: str, status: str = "processing", details: str = "") -> None:
        if self.crm and self.crm.is_configured():
            try:
                self.crm.log_bot_action(self.name, action, status, details)
            except Exception as e:
                logger.error("Failed to log bot action: %s", e)
