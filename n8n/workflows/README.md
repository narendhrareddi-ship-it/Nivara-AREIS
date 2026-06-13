# N8N Workflows

Export-ready workflow JSON files for NIVARA REALTY Phase 1.

## Workflows

| File | Trigger | Purpose |
|------|---------|---------|
| `daily_market_pipeline.json` | Daily 6 AM IST | Market analysis + competitor intel |
| `lead_intake_webhook.json` | POST webhook | Capture leads from forms/ads |
| `crm_sync.json` | Hourly | Sync new leads to CRM agents |
| `analytics_collector.json` | Daily 11 PM IST | Collect mock ad performance data |
| `social_video_publish.json` | Daily 10 AM IST | Publish Higgsfield videos to social |

## Import Instructions

1. Start N8N: `docker compose up -d n8n`
2. Open http://localhost:5678 (default: admin/changeme)
3. Go to **Workflows** → **Import from File**
4. Select each JSON file from this directory
5. Configure environment variables in **Settings → Variables**:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
6. Activate each workflow after import

## Testing Lead Intake Webhook

```bash
curl -X POST http://localhost:5678/webhook/lead-intake \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Lead",
    "phone": "+919999999999",
    "email": "test@example.com",
    "source": "website",
    "city": "Chennai",
    "budget_min": 5000000,
    "budget_max": 8000000,
    "property_type": "apartment"
  }'
```

## Notes

- Agent orchestrator calls use `host.docker.internal` — adjust for Linux if needed
- Phase 1 uses mock analytics; replace Code node with real API integrations in Phase 3
