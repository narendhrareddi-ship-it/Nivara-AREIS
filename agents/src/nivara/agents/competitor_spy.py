"""Competitor Spy Agent — competitor intelligence."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent


from nivara.regions import DEFAULT_REGION


class CompetitorSpyAgent(BaseAgent):
    name = "CompetitorSpy"
    role = "Monitors competitor projects, pricing, and marketing activity"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        competitors: list[dict[str, Any]] = []

        if self.crm.is_configured():
            competitors = self.crm.get_competitors(city=region)

        prompt = (
            f"Competitive intelligence report for {region}.\n"
            f"Known competitors in CRM: {competitors}\n\n"
            "Identify: pricing gaps, differentiation opportunities, "
            "and counter-positioning for NIVARA projects."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "competitors": competitors,
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: report},
            "next_agent": "CMO",
        }
