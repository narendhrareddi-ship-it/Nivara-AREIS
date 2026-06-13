"""WhatsApp Agent — handlesConversational nurturing and lead scoring."""

from __future__ import annotations

import os
from typing import Any

import httpx

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class WhatsAppAgent(BaseAgent):
    name = "WhatsAppAgent"
    role = "Handles conversational lead nurturing and real-time scoring via WhatsApp"

    def __init__(self, llm: Any, crm: Any) -> None:
        super().__init__(llm, crm)
        self.mcp_url = os.getenv("WHATSAPP_MCP_URL", "http://localhost:8004")

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        leads = state.get("leads") or []
        
        if not leads:
            return {
                "agent_outputs": {**state.get("agent_outputs", {}), self.name: "No leads to process for WhatsApp nurturing."},
                "next_agent": "EmailMarketer",
            }

        results = []
        async with httpx.AsyncClient() as client:
            for lead in leads:
                phone = lead.get("phone")
                if not phone:
                    continue
                
                # Call MCP to score lead based on conversation
                try:
                    response = await client.post(
                        f"{self.mcp_url}/call",
                        json={"name": "score_lead", "arguments": {"phone": phone}}
                    )
                    if response.status_code == 200:
                        score_data = response.json().get("result", {})
                        score = score_data.get("score", 0)
                        tier = score_data.get("tier", "cold")
                        results.append(f"Lead {phone}: Score {score} ({tier})")
                except Exception as e:
                    results.append(f"Lead {phone}: Error scoring - {str(e)}")

        summary = "\n".join(results) if results else "No WhatsApp activity found for provided leads."
        
        # Generate nurturing strategy based on scores
        prompt = (
            f"Create a WhatsApp nurturing strategy for these leads in {region}:\n\n"
            f"{summary}\n\n"
            "Recommend: Personalized messaging hooks, urgency triggers, and a follow-up cadence."
        )
        
        strategy = await self.llm.generate(prompt, system=self.system_prompt(region))
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: strategy},
            "next_agent": "EmailMarketer",
        }
