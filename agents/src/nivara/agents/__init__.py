"""Agent registry."""

from nivara.agents.analytics import AnalyticsAgent
from nivara.agents.ceo import CEOAgent
from nivara.agents.cmo import CMOAgent
from nivara.agents.competitor_spy import CompetitorSpyAgent
from nivara.agents.content_strategist import ContentStrategistAgent
from nivara.agents.coo import COOAgent
from nivara.agents.copywriter import CopywriterAgent
from nivara.agents.crm import CRMAgent
from nivara.agents.email_marketer import EmailMarketerAgent
from nivara.agents.lead_qualification import LeadQualificationAgent
from nivara.agents.location_scout import LocationScoutAgent
from nivara.agents.market_analyst import MarketAnalystAgent
from nivara.agents.paid_ads_manager import PaidAdsManagerAgent
from nivara.agents.regulatory_watch import RegulatoryWatchAgent
from nivara.agents.sales_coach import SalesCoachAgent
from nivara.agents.seo_agent import SEOAgent
from nivara.agents.social_media_manager import SocialMediaManagerAgent
from nivara.agents.whatsapp_agent import WhatsAppAgent
from nivara.agents.appointment_scheduler import AppointmentSchedulerAgent
from nivara.agents.visual_designer import VisualDesignerAgent

__all__ = [
    "CEOAgent",
    "COOAgent",
    "CMOAgent",
    "MarketAnalystAgent",
    "RegulatoryWatchAgent",
    "LocationScoutAgent",
    "CompetitorSpyAgent",
    "ContentStrategistAgent",
    "CopywriterAgent",
    "SEOAgent",
    "SocialMediaManagerAgent",
    "PaidAdsManagerAgent",
    "LeadQualificationAgent",
    "SalesCoachAgent",
    "WhatsAppAgent",
    "EmailMarketerAgent",
    "AppointmentSchedulerAgent",
    "VisualDesignerAgent",
    "CRMAgent",
    "AnalyticsAgent",
]
