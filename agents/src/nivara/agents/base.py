"""Base agent types and shared state."""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

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
    final_report: str


class BaseAgent:
    name: str = "BaseAgent"
    role: str = "Base agent"

    def __init__(self, llm: Any, crm: Any) -> None:
        self.llm = llm
        self.crm = crm

    def system_prompt(self, region: str = "Chennai") -> str:
        return (
            f"You are the {self.name} agent for NIVARA REALTY, a digital marketing agency "
            f"specializing in real estate in {region}, Tamil Nadu, and Andhra Pradesh. "
            f"Role: {self.role}. Provide concise, actionable insights."
        )

    async def run(self, state: AgentState) -> dict[str, Any]:
        raise NotImplementedError

    def log_action(self, action: str, status: str = "processing", details: str = "") -> None:
        if self.crm and self.crm.is_configured():
            try:
                self.crm.log_bot_action(self.name, action, status, details)
            except Exception as e:
                logger.error("Failed to log bot action: %s", e)
