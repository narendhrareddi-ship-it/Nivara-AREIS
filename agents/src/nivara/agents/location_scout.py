"""Location Scout Agent — micro-market analysis for Bangalore corridors."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import BANGALORE_CORRIDORS, DEFAULT_REGION


class LocationScoutAgent(BaseAgent):
    name = "LocationScout"
    role = "Analyzes Bangalore micro-markets, corridor demand, and site-location fit"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        market_insight = state.get("agent_outputs", {}).get("MarketAnalyst", "")
        projects: list[dict[str, Any]] = []

        if self.crm.is_configured():
            projects = self.crm.get_projects(city=region)

        corridors = BANGALORE_CORRIDORS
        prompt = (
            f"Micro-market scouting report for NIVARA REALTY in Bangalore.\n"
            f"Priority corridors: {', '.join(corridors)}\n"
            f"Active projects in CRM: {len(projects)}\n"
            f"Sample listings: {projects[:3]}\n"
            f"Market analyst context:\n{market_insight[:900]}\n\n"
            "For each corridor cover: price/sqft range, infrastructure catalysts "
            "(metro, tech parks, airport corridor), buyer profile, and top 2 positioning angles."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: report},
            "next_agent": "CompetitorSpy",
        }
