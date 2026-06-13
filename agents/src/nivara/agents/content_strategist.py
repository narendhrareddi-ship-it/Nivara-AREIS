"""Content Strategist Agent — content calendar and messaging."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class ContentStrategistAgent(BaseAgent):
    name = "ContentStrategist"
    role = "Plans content calendar, ad copy, and social media strategy"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        market_insight = state.get("agent_outputs", {}).get("MarketAnalyst", "")

        prompt = (
            f"Create a weekly content strategy for NIVARA REALTY in {region}.\n"
            f"Market context: {market_insight[:800]}\n\n"
            "Include: 5 post ideas (FB/IG/LinkedIn), 2 ad headline variants, "
            "WhatsApp nurture message template, and Kannada/English mix recommendations."
        )

        strategy = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: strategy},
            "next_agent": "Copywriter",
        }
