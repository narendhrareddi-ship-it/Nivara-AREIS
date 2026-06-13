# NIVARA Agents

LangGraph-based agent orchestration for NIVARA REALTY digital marketing.

## Phase 1 + 2 Agents (Implemented)

- **CEO** — Executive briefing synthesis
- **MarketAnalyst** — Market trends (Chennai/Andhra)
- **CompetitorSpy** — Competitor intelligence
- **ContentStrategist** — Content calendar and copy
- **SEOAgent** — Local SEO strategy
- **VisualDesigner** — Higgsfield photo-to-video generation
- **SocialMediaManager** — Social posting with video support
- **LeadQualification** — Lead scoring
- **WhatsAppAgent** — Conversational lead nurturing
- **AppointmentScheduler** — Site visit scheduling
- **CRM** — Lifecycle management
- **Analytics** — Campaign ROI analysis

## Setup

```bash
cd agents
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e .
cp .env.example .env     # Add Supabase keys
```

## Run Orchestrator

```bash
# Ensure Ollama is running (docker compose up ollama)
ollama pull llama3.2

# Start API server
nivara-orchestrator
# or: python -m nivara.main
```

API: http://localhost:8000/docs

## Test

```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task": "daily_market_analysis", "region": "Chennai"}'
```
