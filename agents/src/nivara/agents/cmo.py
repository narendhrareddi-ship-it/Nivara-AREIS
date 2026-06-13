"""CMO Agent — brand strategy and campaign portfolio management."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION, market_scope


class CMOAgent(BaseAgent):
    name = "CMO"
    role = "Defines brand positioning, campaign themes, and channel mix for Bangalore luxury real estate"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        competitor_intel = state.get("agent_outputs", {}).get("CompetitorSpy", "")
        location_insight = state.get("agent_outputs", {}).get("LocationScout", "")
        regulatory = state.get("agent_outputs", {}).get("RegulatoryWatch", "")

        prompt = (
            f"CMO brand and campaign strategy for NIVARA REALTY in {market_scope(region)}.\n\n"
            f"Competitive landscape:\n{competitor_intel[:600]}\n\n"
            f"Location insights:\n{location_insight[:500]}\n\n"
            f"Regulatory context:\n{regulatory[:400]}\n\n"
            "Deliver: brand positioning statement, 3 campaign themes for Bangalore buyers, "
            "channel budget split (organic vs paid vs nurture), and messaging guardrails."
        )

        strategy = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: strategy},
            "next_agent": "ContentStrategist",
        }
