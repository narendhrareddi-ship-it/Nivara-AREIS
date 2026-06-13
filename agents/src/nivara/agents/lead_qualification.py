"""Lead Qualification Agent — scores and qualifies inbound leads."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class LeadQualificationAgent(BaseAgent):
    name = "LeadQualification"
    role = "Scores leads based on budget, intent, and fit with NIVARA projects"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        leads = state.get("leads") or []

        if not leads and self.crm.is_configured():
            leads = self.crm.get_leads(status="new", limit=10)

        prompt = (
            f"Qualify these real estate leads for NIVARA ({region}):\n"
            f"{leads}\n\n"
            "For each lead: assign score 0-100, status recommendation, "
            "best matching project, and next action. Focus on Bangalore budgets."
        )

        qualification = await self.llm.generate(prompt, system=self.system_prompt(region))

        if self.crm.is_configured() and leads:
            for lead in leads[:5]:
                self.crm.log_activity({
                    "lead_id": lead.get("id"),
                    "activity_type": "ai_action",
                    "title": "AI lead qualification",
                    "description": qualification[:500],
                    "performed_by": "ai",
                    "agent_name": self.name,
                })

        return {
            "leads": leads,
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: qualification},
            "next_agent": "SalesCoach",
        }
