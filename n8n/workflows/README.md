# N8N Workflows (Phase 5)

Export-ready workflow JSON for **Bangalore** real estate — 20-agent pipeline.

## Workflows

| File | Trigger | Purpose |
|------|---------|---------|
| `daily_market_pipeline.json` | Daily 6 AM IST | Full 20-agent pipeline via orchestrator :8000 |
| `lead_intake_webhook.json` | POST webhook | Capture leads + trigger qualification agents |
| `crm_sync.json` | Hourly | Sync new leads to CRM / WhatsApp agents |
| `analytics_collector.json` | Daily 11 PM IST | Ad performance + Analytics/COO/CEO |
| `social_video_publish.json` | Daily 10 AM IST | Publish Gemini Veo videos to social |

## Import Instructions

1. Start N8N: `docker compose up -d n8n`
2. Open http://localhost:5678 (default: admin/changeme)
3. Go to **Workflows** → **Import from File**
4. Select each JSON file from this directory
5. Configure Postgres credentials (Supabase pooler) in n8n
6. Set `ORCHESTRATOR_URL` if not using `host.docker.internal:8000`
7. Activate each workflow after import

## Testing Lead Intake Webhook

```bash
curl -X POST http://localhost:5678/webhook/lead-intake \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Lead",
    "phone": "+919999999999",
    "email": "test@example.com",
    "source": "website",
    "city": "Bangalore",
    "state": "Karnataka",
    "budget_min": 5000000,
    "budget_max": 8000000,
    "property_type": "apartment"
  }'
```

## Notes

- Orchestrator port is **8000** (updated from Phase 1 port 8005)
- Default region is **Bangalore** / Karnataka
- For Render production, replace `host.docker.internal` URLs with HTTPS Render endpoints
- See **[docs/PHASE5.md](../docs/PHASE5.md)** for cloud LLM and API key setup
