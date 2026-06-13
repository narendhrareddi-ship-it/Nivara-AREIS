"""Regulatory Watch Agent — Karnataka RERA and Bangalore development compliance."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION, market_scope


class RegulatoryWatchAgent(BaseAgent):
    name = "RegulatoryWatch"
    role = "Tracks Karnataka RERA, BBMP, and BDA compliance for Bangalore projects"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        market_insight = state.get("agent_outputs", {}).get("MarketAnalyst", "")
        projects: list[dict[str, Any]] = []

        if self.crm.is_configured():
            projects = self.crm.get_projects(city=region)

        prompt = (
            f"Regulatory compliance brief for NIVARA REALTY in {market_scope(region)}.\n"
            f"Active projects in CRM: {len(projects)}\n"
            f"Market context:\n{market_insight[:700]}\n\n"
            "Cover: Karnataka RERA registration checks, BBMP/BDA approval status risks, "
            "mandatory disclosure in ads, stamp duty/registration updates, and "
            "compliance flags for Bangalore corridor marketing."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: report},
            "next_agent": "LocationScout",
        }
