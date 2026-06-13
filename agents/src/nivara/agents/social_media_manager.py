"""Social Media Manager Agent — coordinates FB/IG/LinkedIn posting and engagement."""

from __future__ import annotations

from typing import Any
import httpx

from nivara.agents.base import AgentState, BaseAgent


class SocialMediaManagerAgent(BaseAgent):
    name = "SocialMediaManager"
    role = "Manages social media presence, posting schedules, and engagement tracking"

    def __init__(self, llm: Any, crm: Any) -> None:
        super().__init__(llm, crm)
        self.mcp_url = "http://localhost:8003"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        content_strategy = state.get("agent_outputs", {}).get("ContentStrategist", "")

        if not content_strategy:
            return {
                "agent_outputs": {**state.get("agent_outputs", {}), self.name: "No content strategy available to execute."},
            "next_agent": "LeadQualification",
            }

        # Use the content strategy to generate platform-specific posts
        prompt = (
            f"Translate the following content strategy for {region} into specific social media posts:\n\n"
            f"{content_strategy[:1500]}\n\n"
            "Provide a table with: Platform (FB, IG, LinkedIn, X), Post Copy, Image Brief, and Suggested Posting Time."
        )
        
        social_plan = await self.llm.generate(prompt, system=self.system_prompt(region))
        
        # In a fully autonomous mode, we would call the MCP to schedule these posts
        # For now, we'll log the intent to the CRM
        if self.crm.is_configured():
            self.crm.log_activity({
                "activity_type": "social_media",
                "title": "Social Media Plan Generated",
                "description": f"Plan generated for {region} based on content strategy.",
                "performed_by": "ai",
                "agent_name": self.name,
            })

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: social_plan},
            "next_agent": "CRM",
        }
