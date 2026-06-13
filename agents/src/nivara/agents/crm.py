"""CRM Agent — manages lead lifecycle and follow-ups."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent


class CRMAgent(BaseAgent):
    name = "CRM"
    role = "Manages lead lifecycle, follow-ups, and CRM activity logging"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        leads = state.get("leads") or []
        qualification = state.get("agent_outputs", {}).get("LeadQualification", "")

        prompt = (
            f"CRM action plan for {len(leads)} leads in {region}.\n"
            f"Qualification summary: {qualification[:800]}\n\n"
            "Recommend: follow-up schedule, WhatsApp templates, "
            "site visit scheduling priorities, and CRM status updates."
        )

        crm_plan = await self.llm.generate(prompt, system=self.system_prompt(region))

        if self.crm.is_configured():
            self.crm.log_activity({
                "activity_type": "ai_action",
                "title": "CRM sync completed",
                "description": crm_plan[:500],
                "performed_by": "ai",
                "agent_name": self.name,
            })

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: crm_plan},
            "next_agent": "Analytics",
        }
