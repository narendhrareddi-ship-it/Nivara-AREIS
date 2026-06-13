"""Market Analyst Agent — local market trends and pricing."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent


from nivara.regions import DEFAULT_REGION


class MarketAnalystAgent(BaseAgent):
    name = "MarketAnalyst"
    role = "Analyzes Bangalore real estate market trends, pricing, and demand"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        projects: list[dict[str, Any]] = []

        if self.crm.is_configured():
            projects = self.crm.get_projects(city=region)

        prompt = (
            f"Analyze the real estate market in {region}.\n"
            f"Active projects: {len(projects)} listings in CRM.\n"
            f"Project data sample: {projects[:3]}\n\n"
            "Cover: price trends, hot micro-markets (Whitefield, Sarjapur, Electronic City, "
            "North Bangalore), buyer sentiment, and recommended campaign focus areas."
        )

        analysis = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: analysis},
            "next_agent": "RegulatoryWatch",
        }
