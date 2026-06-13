"""Copywriter Agent — ad copy, landing pages, and nurture sequences."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent


class CopywriterAgent(BaseAgent):
    name = "Copywriter"
    role = "Writes high-converting ad copy, landing page blocks, and email nurture sequences"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        content_strategy = state.get("agent_outputs", {}).get("ContentStrategist", "")
        location_insight = state.get("agent_outputs", {}).get("LocationScout", "")
        competitor_intel = state.get("agent_outputs", {}).get("CompetitorSpy", "")

        prompt = (
            f"Write conversion-focused copy for NIVARA REALTY in {region}.\n\n"
            f"Content strategy:\n{content_strategy[:800]}\n\n"
            f"Location insights:\n{location_insight[:500]}\n\n"
            f"Competitive context:\n{competitor_intel[:500]}\n\n"
            "Deliver:\n"
            "1) 3 Meta/Google ad variants (headline + primary text + CTA)\n"
            "2) Landing page hero + 3 benefit bullets\n"
            "3) 2-email nurture sequence (subject + body, Tamil/English mix)\n"
            "4) WhatsApp opener for cold leads"
        )

        copy = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: copy},
            "next_agent": "SEOAgent",
        }
