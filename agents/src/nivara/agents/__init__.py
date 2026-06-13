"""Agent registry."""

from nivara.agents.analytics import AnalyticsAgent
from nivara.agents.ceo import CEOAgent
from nivara.agents.competitor_spy import CompetitorSpyAgent
from nivara.agents.content_strategist import ContentStrategistAgent
from nivara.agents.crm import CRMAgent
from nivara.agents.lead_qualification import LeadQualificationAgent
from nivara.agents.market_analyst import MarketAnalystAgent
from nivara.agents.seo_agent import SEOAgent
from nivara.agents.social_media_manager import SocialMediaManagerAgent
from nivara.agents.whatsapp_agent import WhatsAppAgent
from nivara.agents.appointment_scheduler import AppointmentSchedulerAgent
from nivara.agents.visual_designer import VisualDesignerAgent

__all__ = [
    "CEOAgent",
    "MarketAnalystAgent",
    "CompetitorSpyAgent",
    "ContentStrategistAgent",
    "SEOAgent",
    "SocialMediaManagerAgent",
    "LeadQualificationAgent",
    "WhatsAppAgent",
    "AppointmentSchedulerAgent",
    "VisualDesignerAgent",
    "CRMAgent",
    "AnalyticsAgent",
]
