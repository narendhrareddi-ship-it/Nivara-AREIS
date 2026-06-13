"""Analytics Agent — campaign performance and ROI analysis."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent


class AnalyticsAgent(BaseAgent):
    name = "Analytics"
    role = "Analyzes campaign performance, ROI, and channel effectiveness"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        analytics: list[dict[str, Any]] = []
        campaigns: list[dict[str, Any]] = []

        if self.crm.is_configured():
            analytics = self.crm.get_ad_performance(days=7)
            campaigns = self.crm.get_campaigns(status="active")

        prompt = (
            f"Analytics report for NIVARA REALTY ({region}).\n"
            f"Active campaigns: {len(campaigns)}\n"
            f"Recent ad performance records: {analytics[:10]}\n\n"
            "Provide: channel ROI comparison, CPL trends, budget reallocation advice, "
            "and mock-data caveats for Phase 1."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "analytics": analytics,
            "campaigns": campaigns,
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: report},
            "next_agent": "CEO",
        }
