"""CEO Agent — strategic orchestration and daily briefing."""

from __future__ import annotations

from typing import Any

from nivara.agents.base import AgentState, BaseAgent
from nivara.regions import DEFAULT_REGION


class CEOAgent(BaseAgent):
    name = "CEO"
    role = "Executive strategist who synthesizes all agent outputs into actionable decisions"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", DEFAULT_REGION)
        outputs = state.get("agent_outputs", {})

        prompt = (
            f"Create a daily executive briefing for NIVARA REALTY ({region}).\n\n"
            f"Agent reports:\n"
            + "\n".join(f"- {k}: {v[:500]}" for k, v in outputs.items())
            + "\n\nProvide: top 3 priorities, budget recommendations, and risk flags."
        )

        report = await self.llm.generate(prompt, system=self.system_prompt(region))
        return {
            "agent_outputs": {**outputs, self.name: report},
            "final_report": report,
            "next_agent": "__end__",
        }
