"""Appointment Scheduler Agent — manages site visits and call scheduling."""

from __future__ import annotations

from typing import Any
import httpx

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class AppointmentSchedulerAgent(BaseAgent):
    name = "AppointmentScheduler"
    role = "Coordinates site visits, call scheduling, and calendar synchronization"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        leads = state.get("leads") or []
        whatsapp_strategy = state.get("agent_outputs", {}).get("WhatsAppAgent", "")

        if not leads:
            return {
                "agent_outputs": {**state.get("agent_outputs", {}), self.name: "No leads available for scheduling."},
                "next_agent": "CRM",
            }

        # In Phase 1/2, we identify 'hot' leads and propose scheduling slots
        prompt = (
            f"Based on the WhatsApp strategy for {region}:\n\n"
            f"{whatsapp_strategy[:1000]}\n\n"
            f"For the current leads, propose a site visit schedule. "
            "Focus on high-intent leads. Suggest optimal days/times for Bangalore site visits."
        )
        
        schedule_plan = await self.llm.generate(prompt, system=self.system_prompt(region))
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: schedule_plan},
            "next_agent": "CRM",
        }
