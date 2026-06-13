# NIVARA REALTY — Agent Roster (20 Agents)

Full digital marketing agency architecture. All 20 agents are implemented. **Market focus: Bangalore only.**

## Executive Layer

| # | Agent | Role | Status |
|---|-------|------|--------|
| 1 | **CEO** | Strategic synthesis, daily briefings, budget decisions | ✅ Implemented |
| 2 | **COO** | Operations, workflow optimization, SLA monitoring | ✅ Phase 4 |
| 3 | **CMO** | Brand strategy, campaign portfolio management | ✅ Phase 4 |

## Market Intelligence

| # | Agent | Role | Status |
|---|-------|------|--------|
| 4 | **MarketAnalyst** | Bangalore trends, pricing, demand signals | ✅ Implemented |
| 5 | **CompetitorSpy** | Competitor projects, pricing, ad monitoring | ✅ Implemented |
| 6 | **LocationScout** | Micro-market analysis (Whitefield, Sarjapur, North Bangalore) | ✅ Phase 3 |
| 7 | **RegulatoryWatch** | Karnataka RERA / BBMP compliance tracking | ✅ Phase 4 |

## Content & Creative

| # | Agent | Role | Status |
|---|-------|------|--------|
| 8 | **ContentStrategist** | Content calendar, messaging, Kannada/English mix | ✅ Implemented |
| 9 | **Copywriter** | Ad copy, landing pages, email sequences | ✅ Phase 3 |
| 10 | **VisualDesigner** | Image/video briefs, Gemini Veo photo-to-video | ✅ Implemented |
| 11 | **SEOAgent** | Local SEO, Google Business, schema markup | ✅ Implemented |

## Lead & Sales

| # | Agent | Role | Status |
|---|-------|------|--------|
| 12 | **LeadQualification** | Score leads, match to projects | ✅ Implemented |
| 13 | **CRM** | Lifecycle management, follow-ups | ✅ Implemented |
| 14 | **SalesCoach** | Objection handling, negotiation scripts | ✅ Phase 4 |
| 15 | **AppointmentScheduler** | Site visit and call scheduling | ✅ Implemented |

## Channels & Analytics

| # | Agent | Role | Status |
|---|-------|------|--------|
| 16 | **Analytics** | Campaign ROI, CPL, channel performance | ✅ Implemented |
| 17 | **SocialMediaManager** | FB/IG/LinkedIn/X posting with video support | ✅ Implemented |
| 18 | **PaidAdsManager** | Google/Meta ad optimization | ✅ Phase 3 |
| 19 | **WhatsAppAgent** | Conversational lead nurturing | ✅ Implemented |
| 20 | **EmailMarketer** | Drip campaigns, newsletters | ✅ Phase 3 |

## Agent Graph (Bangalore — 20 agents)

```
MarketAnalyst → RegulatoryWatch → LocationScout → CompetitorSpy → CMO
  → ContentStrategist → Copywriter → SEOAgent → VisualDesigner
  → SocialMediaManager → PaidAdsManager → LeadQualification → SalesCoach
  → WhatsAppAgent → EmailMarketer → AppointmentScheduler → CRM
  → Analytics → COO → CEO
```

## Market configuration

Default region is set in [`agents/src/nivara/regions.py`](../agents/src/nivara/regions.py):

- `DEFAULT_REGION = "Bangalore"`
- `DEFAULT_STATE = "Karnataka"`
- Priority corridors: Whitefield, Sarjapur Road, Electronic City, HSR, Koramangala, Hebbal, Yelahanka, Devanahalli

## Agent ↔ MCP Mapping

| Agent | MCP Server | Tools |
|-------|-----------|-------|
| CRM, LeadQualification | crm-mcp | list_leads, update_lead, log_activity |
| CompetitorSpy | browser-mcp | scrape_competitor, search_listings |
| VisualDesigner | veo-mcp | upload_site_photo, photo_to_video |
| SocialMediaManager | social-mcp, veo-mcp | publish_post, publish_video_to_social |
| PaidAdsManager | — | CRM campaigns + ad_performance tables |
| EmailMarketer | — | CRM activity log (+ optional EMAIL_API_URL) |
| WhatsAppAgent | whatsapp-mcp | handle_message, score_lead |
