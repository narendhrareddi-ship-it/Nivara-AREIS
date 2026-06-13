"""Location Scout Agent — micro-market analysis for Chennai/Andhra corridors."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent

CORRIDORS = {
    "Chennai": ["OMR", "ECR", "GST Road", "Velachery", "Sholinganallur", "Porur"],
    "Andhra Pradesh": ["Amaravati", "Vizag Beach Road", "Guntur", "Tirupati"],
}


class LocationScoutAgent(BaseAgent):
    name = "LocationScout"
    role = "Analyzes micro-markets, corridor demand, and site-location fit for NIVARA projects"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        market_insight = state.get("agent_outputs", {}).get("MarketAnalyst", "")
        projects: list[dict[str, Any]] = []

        if self.crm.is_configured():
            projects = self.crm.get_projects(city=region)

        corridors = CORRIDORS.get(region, CORRIDORS["Chennai"])
        prompt = (
            f"Micro-market scouting report for NIVARA REALTY in {region}.\n"
            f"Priority corridors: {', '.join(corridors)}\n"
            f"Active projects in CRM: {len(projects)}\n"
            f"Sample listings: {projects[:3]}\n"
            f"Market analyst context:\n{market_insight[:900]}\n\n"
            "For each corridor cover: price/sqft range, infrastructure catalysts "
            "(metro, IT parks, highways), buyer profile, and top 2 project positioning angles."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: report},
            "next_agent": "CompetitorSpy",
        }
