"""LangGraph orchestrator — full 20-agent Bangalore pipeline."""

from __future__ import annotations

import logging
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from nivara.agents import (
    AnalyticsAgent,
    CEOAgent,
    CMOAgent,
    COOAgent,
    CompetitorSpyAgent,
    ContentStrategistAgent,
    CopywriterAgent,
    CRMAgent,
    EmailMarketerAgent,
    LeadQualificationAgent,
    LocationScoutAgent,
    MarketAnalystAgent,
    PaidAdsManagerAgent,
    RegulatoryWatchAgent,
    SEOAgent,
    SalesCoachAgent,
    SocialMediaManagerAgent,
    WhatsAppAgent,
    VisualDesignerAgent,
    AppointmentSchedulerAgent,
)
from nivara.agents.base import AgentState
from nivara.db.supabase_client import SupabaseCRM
from nivara.llm.ollama_client import OllamaClient
from nivara.regions import DEFAULT_REGION

logger = logging.getLogger(__name__)

AgentName = Literal[
    "MarketAnalyst",
    "RegulatoryWatch",
    "LocationScout",
    "CompetitorSpy",
    "CMO",
    "ContentStrategist",
    "Copywriter",
    "SEOAgent",
    "VisualDesigner",
    "SocialMediaManager",
    "PaidAdsManager",
    "LeadQualification",
    "SalesCoach",
    "WhatsAppAgent",
    "EmailMarketer",
    "AppointmentScheduler",
    "CRM",
    "Analytics",
    "COO",
    "CEO",
]

PIPELINE_ORDER: list[str] = [
    "MarketAnalyst",
    "RegulatoryWatch",
    "LocationScout",
    "CompetitorSpy",
    "CMO",
    "ContentStrategist",
    "Copywriter",
    "SEOAgent",
    "VisualDesigner",
    "SocialMediaManager",
    "PaidAdsManager",
    "LeadQualification",
    "SalesCoach",
    "WhatsAppAgent",
    "EmailMarketer",
    "AppointmentScheduler",
    "CRM",
    "Analytics",
    "COO",
    "CEO",
]


class AgentOrchestrator:
    def __init__(
        self,
        llm: OllamaClient | None = None,
        crm: SupabaseCRM | None = None,
    ) -> None:
        self.llm = llm or OllamaClient()
        self.crm = crm or SupabaseCRM()
        self._agents: dict[str, Any] = {
            "MarketAnalyst": MarketAnalystAgent(self.llm, self.crm),
            "RegulatoryWatch": RegulatoryWatchAgent(self.llm, self.crm),
            "LocationScout": LocationScoutAgent(self.llm, self.crm),
            "CompetitorSpy": CompetitorSpyAgent(self.llm, self.crm),
            "CMO": CMOAgent(self.llm, self.crm),
            "ContentStrategist": ContentStrategistAgent(self.llm, self.crm),
            "Copywriter": CopywriterAgent(self.llm, self.crm),
            "SEOAgent": SEOAgent(self.llm, self.crm),
            "VisualDesigner": VisualDesignerAgent(self.llm, self.crm),
            "SocialMediaManager": SocialMediaManagerAgent(self.llm, self.crm),
            "PaidAdsManager": PaidAdsManagerAgent(self.llm, self.crm),
            "LeadQualification": LeadQualificationAgent(self.llm, self.crm),
            "SalesCoach": SalesCoachAgent(self.llm, self.crm),
            "WhatsAppAgent": WhatsAppAgent(self.llm, self.crm),
            "EmailMarketer": EmailMarketerAgent(self.llm, self.crm),
            "AppointmentScheduler": AppointmentSchedulerAgent(self.llm, self.crm),
            "CRM": CRMAgent(self.llm, self.crm),
            "Analytics": AnalyticsAgent(self.llm, self.crm),
            "COO": COOAgent(self.llm, self.crm),
            "CEO": CEOAgent(self.llm, self.crm),
        }
        self.graph = self._build_graph()

    def _make_node(self, agent_name: str):
        async def node(state: AgentState) -> dict[str, Any]:
            agent = self._agents[agent_name]
            logger.info("Running agent: %s", agent_name)

            agent.log_action("Starting task", "processing", f"Agent {agent_name} is now active.")

            try:
                result = await agent.run(state)
                agent.log_action("Task completed", "success", f"Agent {agent_name} finished execution.")
                return result
            except Exception as e:
                agent.log_action("Task failed", "error", str(e))
                raise e

        return node

    def _route_next(self, state: AgentState) -> str:
        return state.get("next_agent", "__end__")

    def _build_graph(self) -> Any:
        workflow: StateGraph = StateGraph(AgentState)

        for name in self._agents:
            workflow.add_node(name, self._make_node(name))

        workflow.set_entry_point("MarketAnalyst")

        path_map: dict[str, Any] = {name: name for name in self._agents}
        path_map["__end__"] = END

        for name in self._agents:
            workflow.add_conditional_edges(name, self._route_next, path_map)

        return workflow.compile()

    async def run(
        self,
        task: str = "daily_market_analysis",
        region: str = DEFAULT_REGION,
        leads: list[dict[str, Any]] | None = None,
        agents: list[str] | None = None,
        media_assets: list[dict[str, Any]] | None = None,
        project_id: str | None = None,
        auto_publish_social: bool = True,
    ) -> AgentState:
        initial_state: AgentState = {
            "task": task,
            "region": region,
            "leads": leads or [],
            "media_assets": media_assets or [],
            "media_videos": [],
            "project_id": project_id or "",
            "auto_publish_social": auto_publish_social,
            "agent_outputs": {},
            "messages": [],
        }

        if agents:
            return await self._run_subset(initial_state, agents)

        result: AgentState = await self.graph.ainvoke(initial_state)
        return result

    async def _run_subset(
        self,
        state: AgentState,
        agent_names: list[str],
    ) -> AgentState:
        current = state
        for name in agent_names:
            if name not in self._agents:
                logger.warning("Unknown agent: %s", name)
                continue
            current = {**current, **await self._agents[name].run(current)}
        return current
