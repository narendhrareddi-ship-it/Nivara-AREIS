# NIVARA REALTY — Agent Roster (20 Agents)

Full digital marketing agency architecture. Phase 1 implements 7 core agents; remaining 13 are documented stubs for future phases.

## Executive Layer

| # | Agent | Role | Phase 1 |
|---|-------|------|---------|
| 1 | **CEO** | Strategic synthesis, daily briefings, budget decisions | ✅ Implemented |
| 2 | **COO** | Operations, workflow optimization, SLA monitoring | 🔲 Stub |
| 3 | **CMO** | Brand strategy, campaign portfolio management | 🔲 Stub |

## Market Intelligence

| # | Agent | Role | Phase 1 |
|---|-------|------|---------|
| 4 | **MarketAnalyst** | Chennai/Andhra trends, pricing, demand signals | ✅ Implemented |
| 5 | **CompetitorSpy** | Competitor projects, pricing, ad monitoring | ✅ Implemented |
| 6 | **LocationScout** | Micro-market analysis (OMR, ECR, Amaravati corridors) | 🔲 Stub |
| 7 | **RegulatoryWatch** | RERA/CRDA compliance tracking | 🔲 Stub |

## Content & Creative

| # | Agent | Role | Phase 1 |
|---|-------|------|---------|
| 8 | **ContentStrategist** | Content calendar, messaging, Tamil/English mix | ✅ Implemented |
| 9 | **Copywriter** | Ad copy, landing pages, email sequences | 🔲 Stub |
| 10 | **VisualDesigner** | Image/video briefs (Canva/manual in Phase 1) | 🔲 Stub |
| 11 | **SEOAgent** | Local SEO, Google Business, schema markup | 🔲 Stub |

## Lead & Sales

| # | Agent | Role | Phase 1 |
|---|-------|------|---------|
| 12 | **LeadQualification** | Score leads, match to projects | ✅ Implemented |
| 13 | **CRM** | Lifecycle management, follow-ups | ✅ Implemented |
| 14 | **SalesCoach** | Objection handling, negotiation scripts | 🔲 Stub |
| 15 | **AppointmentScheduler** | Site visit and call scheduling | 🔲 Stub |

## Channels & Analytics

| # | Agent | Role | Phase 1 |
|---|-------|------|---------|
| 16 | **Analytics** | Campaign ROI, CPL, channel performance | ✅ Implemented |
| 17 | **SocialMediaManager** | FB/IG/LinkedIn/X posting | 🔲 Stub (social-mcp mock) |
| 18 | **PaidAdsManager** | Google/Meta ad optimization | 🔲 Stub |
| 19 | **WhatsAppAgent** | Conversational lead nurturing | 🔲 Stub (whatsapp-mcp mock) |
| 20 | **EmailMarketer** | Drip campaigns, newsletters | 🔲 Stub |

## Phase 1 Agent Graph

```
MarketAnalyst → CompetitorSpy → ContentStrategist → LeadQualification → CRM → Analytics → CEO
```

## Stub Agent Plan (Phase 2-4)

| Phase | Agents to Implement |
|-------|---------------------|
| **Phase 2** | WhatsAppAgent, AppointmentScheduler, SocialMediaManager, SEOAgent |
| **Phase 3** | PaidAdsManager, Copywriter, LocationScout, EmailMarketer |
| **Phase 4** | COO, CMO, SalesCoach, VisualDesigner, RegulatoryWatch |

## Agent ↔ MCP Mapping

| Agent | MCP Server | Tools |
|-------|-----------|-------|
| CRM, LeadQualification | crm-mcp | list_leads, update_lead, log_activity |
| CompetitorSpy | browser-mcp | scrape_competitor, search_listings |
| SocialMediaManager | social-mcp | publish_post, schedule_post |
| WhatsAppAgent | whatsapp-mcp | handle_message, score_lead |
