# Phase 4 — Executive Agents & Bangalore Focus

Phase 4 completes the 20-agent roster and locks the system to **Bangalore-only** analysis.

## Bangalore market focus

All agents, dashboard copy, demo data, and API defaults now use:

| Setting | Value |
|---------|-------|
| Region | `Bangalore` |
| State | `Karnataka` |
| Corridors | Whitefield, Sarjapur, Electronic City, HSR, Koramangala, Hebbal, Yelahanka, Devanahalli |

Chennai and Andhra Pradesh references have been removed from active code paths. To expand to other cities later, update [`agents/src/nivara/regions.py`](../agents/src/nivara/regions.py).

## New Phase 4 agents

| Agent | Role | Pipeline position |
|-------|------|-------------------|
| **RegulatoryWatch** | Karnataka RERA, BBMP/BDA compliance | After MarketAnalyst |
| **CMO** | Brand positioning and campaign themes | After CompetitorSpy |
| **SalesCoach** | Objection handling and closing scripts | After LeadQualification |
| **COO** | SLA monitoring and operational review | After Analytics, before CEO |

## Full 20-agent pipeline

```
MarketAnalyst → RegulatoryWatch → LocationScout → CompetitorSpy → CMO
  → ContentStrategist → Copywriter → SEOAgent → VisualDesigner
  → SocialMediaManager → PaidAdsManager → LeadQualification → SalesCoach
  → WhatsAppAgent → EmailMarketer → AppointmentScheduler → CRM
  → Analytics → COO → CEO
```

## Dashboard updates

- Hero banner: **Bangalore · Karnataka**
- Market overview chips: Bangalore pricing and Whitefield corridor
- Pipeline UI: 20 agents
- All orchestrator calls use `region: "Bangalore"`

## What's next

- Deploy Render backend ([`render.yaml`](../render.yaml)) and update Streamlit secrets
- Create Supabase Storage bucket `media`
- Connect real Meta/WhatsApp/email APIs
- Add Playwright scraping to browser-mcp
