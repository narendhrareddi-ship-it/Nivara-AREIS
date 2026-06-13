"""Email Marketer Agent — drip campaigns and newsletters."""

from __future__ import annotations

import os
from typing import Any

import httpx

from nivara.agents.base import AgentState, BaseAgent


class EmailMarketerAgent(BaseAgent):
    name = "EmailMarketer"
    role = "Runs drip campaigns, newsletters, and lead re-engagement emails"

    def __init__(self, llm: Any, crm: Any) -> None:
        super().__init__(llm, crm)
        self.email_api_url = os.getenv("EMAIL_API_URL", "")
        self.email_api_key = os.getenv("EMAIL_API_KEY", "")

    async def _send_via_api(self, to_email: str, subject: str, body: str) -> str:
        if not self.email_api_url or not self.email_api_key:
            return "mock_sent"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.email_api_url,
                headers={"Authorization": f"Bearer {self.email_api_key}"},
                json={"to": to_email, "subject": subject, "html": body},
            )
            if response.status_code >= 400:
                return f"failed:{response.status_code}"
            return "sent"

    async def run(self, state: AgentState) -> dict[str, Any]:
        region = state.get("region", "Chennai")
        leads = state.get("leads") or []
        copy_pack = state.get("agent_outputs", {}).get("Copywriter", "")
        whatsapp_plan = state.get("agent_outputs", {}).get("WhatsAppAgent", "")

        if not leads and self.crm.is_configured():
            leads = self.crm.get_leads(status=None, limit=10)

        email_leads = [lead for lead in leads if lead.get("email")][:5]

        prompt = (
            f"Design an email marketing program for NIVARA REALTY in {region}.\n"
            f"Leads with email: {len(email_leads)}\n"
            f"Copy assets:\n{copy_pack[:700]}\n"
            f"WhatsApp nurture context:\n{whatsapp_plan[:400]}\n\n"
            "Provide: welcome drip (3 emails), monthly newsletter outline, "
            "re-engagement email for cold leads, and send-time recommendations (IST)."
        )

        program = await self.llm.generate(prompt, system=self.system_prompt(region))
        delivery_log: list[str] = []

        for lead in email_leads:
            email = lead.get("email", "")
            name = lead.get("full_name", "there")
            subject = f"Your {region} property shortlist — NIVARA REALTY"
            body = (
                f"<p>Hi {name},</p>"
                f"<p>Based on your interest in {region} real estate, here are curated options "
                f"from NIVARA REALTY.</p>"
                f"<p>{program[:400]}</p>"
            )
            status = await self._send_via_api(email, subject, body)
            delivery_log.append(f"{email}: {status}")

            if self.crm.is_configured() and lead.get("id"):
                self.crm.log_activity({
                    "lead_id": lead["id"],
                    "activity_type": "email",
                    "title": subject,
                    "description": program[:500],
                    "performed_by": "ai",
                    "agent_name": self.name,
                })

        summary = program
        if delivery_log:
            summary += "\n\nDelivery:\n" + "\n".join(delivery_log)

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), self.name: summary},
            "next_agent": "AppointmentScheduler",
        }
