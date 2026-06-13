"""Sales Coach Agent — objection handling and negotiation scripts."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION, market_scope


class SalesCoachAgent(BaseAgent):
    name = "SalesCoach"
    role = "Coaches sales teams on objections, pricing talks, and Bangalore buyer psychology"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        qualification = state.get("agent_outputs", {}).get("LeadQualification", "")
        ad_copy = state.get("agent_outputs", {}).get("Copywriter", "")
        leads = state.get("leads") or []

        prompt = (
            f"Sales coaching playbook for NIVARA REALTY ({market_scope(region)}).\n"
            f"Leads in pipeline: {len(leads)}\n"
            f"Qualification summary:\n{qualification[:800]}\n"
            f"Approved copy angles:\n{ad_copy[:500]}\n\n"
            "Provide: top 5 objections (price, location, possession, EMI, competitor), "
            "word-for-word rebuttals, negotiation anchors, and site-visit closing scripts "
            "tailored to Bangalore IT/NRI/end-user segments."
        )

        playbook = await self.llm.generate(prompt, system=self.system_prompt(region))

        if self.crm.is_configured():
            self.crm.log_activity({
                "activity_type": "ai_action",
                "title": "Sales coaching playbook updated",
                "description": playbook[:500],
                "performed_by": "ai",
                "agent_name": self.name,
            })

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: playbook},
            "next_agent": "WhatsAppAgent",
        }
