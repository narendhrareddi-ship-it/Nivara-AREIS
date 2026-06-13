"""Paid Ads Manager Agent — Google/Meta campaign optimization."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class PaidAdsManagerAgent(BaseAgent):
    name = "PaidAdsManager"
    role = "Optimizes Google and Meta ad spend, audiences, and creative rotation"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        ad_copy = state.get("agent_outputs", {}).get("Copywriter", "")
        social_summary = state.get("agent_outputs", {}).get("SocialMediaManager", "")
        campaigns: list[dict[str, Any]] = []
        performance: list[dict[str, Any]] = []

        if self.crm.is_configured():
            campaigns = self.crm.get_campaigns(status="active")
            performance = self.crm.get_ad_performance(days=14)

        prompt = (
            f"Paid media optimization plan for NIVARA REALTY ({region}).\n"
            f"Active campaigns: {len(campaigns)}\n"
            f"Recent performance rows: {performance[:8]}\n"
            f"Approved ad copy:\n{ad_copy[:700]}\n"
            f"Organic social context:\n{social_summary[:400]}\n\n"
            "Provide: budget split by channel (Google Search, Meta, YouTube), "
            "audience segments for Bangalore buyers, creative A/B tests, "
            "CPL targets, and pause/scale rules based on 7-day trends."
        )

        plan = await self.llm.generate(prompt, system=self.system_prompt(region))

        if self.crm.is_configured():
            self.crm.log_activity({
                "activity_type": "campaign_touch",
                "title": "Paid ads optimization review",
                "description": plan[:500],
                "performed_by": "ai",
                "agent_name": self.name,
            })

        return {
            "campaigns": campaigns,
            "analytics": performance,
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: plan},
            "next_agent": "LeadQualification",
        }
