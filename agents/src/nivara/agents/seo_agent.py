"""SEO Agent — manages Local SEO, Google Business Profile, and schema markup."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class SEOAgent(BaseAgent):
    name = "SEOAgent"
    role = "Optimizes local search visibility, GMB profiles, and organic real estate traffic"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        market_analysis = state.get("agent_outputs", {}).get("MarketAnalyst", "")

        prompt = (
            f"Develop a local SEO strategy for NIVARA REALTY in {region} based on this market analysis:\n\n"
            f"{market_analysis[:1000]}\n\n"
            "Provide: Target keywords for real estate in this region, GMB optimization tips, "
            "and suggested local backlinks or directory listings."
        )
        
        seo_strategy = await self.llm.generate(prompt, system=self.system_prompt(region))
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: seo_strategy},
            "next_agent": "VisualDesigner",
        }
