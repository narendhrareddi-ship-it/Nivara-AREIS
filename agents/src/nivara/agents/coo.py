"""COO Agent — operations, SLA monitoring, and workflow optimization."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION, market_scope


class COOAgent(BaseAgent):
    name = "COO"
    role = "Monitors agent SLAs, bottlenecks, and operational efficiency across the marketing stack"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        outputs = state.get("agent_outputs", {})
        analytics_report = outputs.get("Analytics", "")
        campaigns = state.get("campaigns") or []
        leads = state.get("leads") or []

        if self.crm.is_configured() and not campaigns:
            campaigns = self.crm.get_campaigns(status="active")

        prompt = (
            f"COO operations review for NIVARA REALTY ({market_scope(region)}).\n"
            f"Agents executed this run: {len(outputs)}\n"
            f"Active campaigns: {len(campaigns)}\n"
            f"Leads in state: {len(leads)}\n"
            f"Analytics summary:\n{analytics_report[:700]}\n\n"
            "Provide: SLA health (response time, publish cadence, lead follow-up), "
            "bottleneck agents, resource reallocation, and 3 operational fixes for this week."
        )

        review = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**outputs, self.name: review},
            "next_agent": "CEO",
        }
